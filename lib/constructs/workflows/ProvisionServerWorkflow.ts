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
import { LambdaInvoke } from "monocdk/aws-stepfunctions-tasks";
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
  readonly discordLayer: LayerVersion;
  readonly serverboiUtilsLayer: LayerVersion;
  readonly tokenBucket: Bucket;
  readonly tokenQueue: Queue;
  readonly serverList: Table;
  readonly webhookList: Table;
  readonly userList: Table;
  readonly awsTable: Table;
  readonly linodeTable: Table;
  readonly cloudApis: LayerVersion;
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
        AWS_TABLE: props.awsTable.tableName,
        LINODE_TABLE: props.linodeTable.tableName,
        DYNAMO_CONTAINER: "serverboi-dynamodb-local",
        LOCALSTACK_CONTAINER: "serverboi-localstack",
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
        USER_TABLE: props.userList.tableName,
        SERVER_TABLE: props.serverList.tableName,
        AWS_TABLE: props.awsTable.tableName,
        LINODE_TABLE: props.linodeTable.tableName,
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
            ExecutionName: "$.ExecutionName",
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
          ExecutionName: "$.ExecutionName",
          InteractionToken: "$.InteractionToken",
          ApplicationID: "$.ApplicationID",
          GuildID: "$.GuildID",
          ServerID: "$.ServerID",
        }
      }
    });

    const endStep = new Succeed(this, "End-Step");

    const stepDefinition = provisionStep;
    provisionStep.next(tokenNodes[0]);

    var i = 0;
    do {
      tokenNodes[i].next(tokenNodes[i + 1]);
      i = i + 1;
    } while (i <= tokenNodes.length - 2);

    tokenNodes[i].next(finishProvisionStep);

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
