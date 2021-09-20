import { Construct, Duration } from "monocdk";
import { LayerVersion } from "monocdk/aws-lambda";
import {
  StateMachine,
  Succeed,
  InputType,
  IntegrationPattern,
  JsonPath,
  TaskInput,
} from "monocdk/aws-stepfunctions";
import { LambdaInvoke, StepFunctionsStartExecution } from "monocdk/aws-stepfunctions-tasks";
import { PolicyStatement } from "monocdk/aws-iam";
import { Table } from "monocdk/aws-dynamodb";
import { GoLambda } from "../GoLambdaConstruct";
import { Bucket } from "monocdk/aws-s3";
import { Queue } from "monocdk/aws-sqs";
import { Secret } from "monocdk/aws-secretsmanager";
import { 
  FinishProvision,
  ProvisionServer,
  PutToken,
 } from "../../../function_uri_list.json"

export interface ProvisionServerProps {
  readonly tokenBucket: Bucket;
  readonly tokenQueue: Queue;
  readonly serverList: Table;
  readonly webhookList: Table;
  readonly ownerList: Table;
  readonly channelList: Table;
  readonly discordToken: string;
  readonly terminationWorkflow: StateMachine;
  readonly provisionConfigurationBucket: Bucket;
}

export class ProvisionServerWorkflow extends Construct {
  public readonly provisionStateMachine: StateMachine;

  constructor(scope: Construct, id: string, props: ProvisionServerProps) {
    super(scope, id);

    const provisionName = "Provision-Lambda-Go";
    const provision = new GoLambda(this, provisionName, {
      name: provisionName,
      bucket: ProvisionServer.bucket,
      object: ProvisionServer.key,
      environment: {
        SERVER_TABLE: props.serverList.tableName,
        OWNER_TABLE: props.ownerList.tableName,
        DISCORD_TOKEN: props.discordToken,
        CONFIGURATION_BUCKET: props.provisionConfigurationBucket.bucketName,
        STAGE: "Prod"
      },
    });
    provision.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:GetObject",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "sts:AssumeRole",
        ],
      })
    );

    const putTokenName = "Put-Token-Lambda-Go";
    const putToken = new GoLambda(this, putTokenName, {
      name: putTokenName,
      bucket: PutToken.bucket,
      object: PutToken.key,
      environment: {
        TOKEN_BUCKET: props.tokenBucket.bucketName,
      },
    });
    putToken.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:PutObject",
        ],
      })
    );

    const disordToken = Secret.fromSecretCompleteArn(
      this,
      "ServerBoi-Discord-Token",
      "arn:aws:secretsmanager:us-west-2:518723822228:secret:ServerBoi-Discord-Token-RBBLnM"
    );

    const finishProvisionName = "Finish-Provision-Go";
    const finishProvision = new GoLambda(this, finishProvisionName, {
      name: finishProvisionName,
      bucket: FinishProvision.bucket,
      object: FinishProvision.key,
      environment: {
        DISCORD_TOKEN: disordToken.secretValue.toString(),
        SERVER_TABLE: props.serverList.tableName,
        CHANNEL_TABLE: props.channelList.tableName,
        WEBHOOK_TABLE: props.webhookList.tableName
      },
    });
    finishProvision.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "dynamodb:Query",
          "dynamodb:GetItem",
          "sts:AssumeRole",
        ],
      })
    );

    //step definitions
    const provisionStep = new LambdaInvoke(this, "Provision-Step", {
      lambdaFunction: provision.lambda,
      inputPath: "$",
      resultPath: "$.ServerID",
      payloadResponseOnly: true
    });

    const tokenNodeNames = ["Wait-For-Download", "Starting-Server-Client"];

    var tokenNodes = new Array<LambdaInvoke>();

    tokenNodeNames.forEach((stageName) => {
      var stage = new LambdaInvoke(this, stageName, {
        lambdaFunction: putToken.lambda,
        integrationPattern: IntegrationPattern.WAIT_FOR_TASK_TOKEN,
        timeout: Duration.hours(1),
        payload: {
          type: InputType.OBJECT,
          value: {
            ExecutionName: TaskInput.fromJsonPathAt("$.ExecutionName").value,
            TaskToken: JsonPath.taskToken,
          },
        },
        resultPath: JsonPath.DISCARD,
      });

      tokenNodes.push(stage);
    });

    const finishProvisionStep = new LambdaInvoke(this, "Finish-Provision-Step", {
      lambdaFunction: finishProvision.lambda,
      resultPath: JsonPath.DISCARD,
      payload: {
        type: InputType.OBJECT,
        value: {
          ExecutionName: TaskInput.fromJsonPathAt("$.ExecutionName").value,
          InteractionToken: TaskInput.fromJsonPathAt("$.InteractionToken").value,
          ApplicationID: TaskInput.fromJsonPathAt("$.ApplicationID").value,
          GuildID: TaskInput.fromJsonPathAt("$.GuildID").value,
          ServerID: TaskInput.fromJsonPathAt("$.ServerID").value,
          Private: TaskInput.fromJsonPathAt("$.Private").value
        }
      }
    });

    const endStep = new Succeed(this, "End-Step");

    const catchFailure = new StepFunctionsStartExecution(this, "Terminate-Failed-Server", {
      stateMachine: props.terminationWorkflow,
      name: "Terminate-Failed-Server",
      input: TaskInput.fromObject({
        Token: TaskInput.fromJsonPathAt("$.InteractionToken").value,
        ApplicationID: TaskInput.fromJsonPathAt("$.ApplicationID").value,
        ServerID: TaskInput.fromJsonPathAt("$.ServerID").value,
        ExecutionName: TaskInput.fromJsonPathAt("$.ExecutionName").value,
        Fallback: true,
      }),
    })

    const stepDefinition = provisionStep;
    provisionStep.next(tokenNodes[0]);

    var i = 0;
    do {
      tokenNodes[i].addCatch(catchFailure)
      tokenNodes[i].next(tokenNodes[i + 1]);
      i = i + 1;
    } while (i <= tokenNodes.length - 2);

    tokenNodes[i].next(finishProvisionStep);

    finishProvisionStep.addCatch(catchFailure)
    finishProvisionStep.next(endStep);

    this.provisionStateMachine = new StateMachine(
      this,
      "Provision-Server-State-Machine",
      {
        definition: stepDefinition,
        stateMachineName: "Provision-Server-Workflow",
      }
    );
  }
}
