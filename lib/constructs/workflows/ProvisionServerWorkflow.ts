import { Construct, Duration } from "monocdk";
import { LayerVersion } from "monocdk/aws-lambda";
import {
  StateMachine,
  Succeed,
  InputType,
  IntegrationPattern,
  JsonPath,
} from "monocdk/aws-stepfunctions";
import { LambdaInvoke } from "monocdk/aws-stepfunctions-tasks";
import { PolicyStatement } from "monocdk/aws-iam";
import { Table } from "monocdk/aws-dynamodb";
import { PythonLambda } from "../PythonLambdaConstruct";
import { Bucket } from "monocdk/aws-s3";
import { Queue } from "monocdk/aws-sqs";
import { Secret } from "monocdk/aws-secretsmanager";

export interface ProvisionServerProps {
  readonly discordLayer: LayerVersion;
  readonly serverboiUtilsLayer: LayerVersion;
  readonly tokenBucket: Bucket;
  readonly tokenQueue: Queue;
  readonly serverList: Table;
  readonly userList: Table;
}

export class ProvisionServerWorkflow extends Construct {
  public readonly provisionStateMachine: StateMachine;

  constructor(scope: Construct, id: string, props: ProvisionServerProps) {
    super(scope, id);

    const provisionName = "Provision-Lambda";
    const provision = new PythonLambda(this, provisionName, {
      name: provisionName,
      codePath: "lambdas/handlers/provision_workflow/provision_lambda/",
      handler: "provision.main.lambda_handler",
      layers: [props.discordLayer, props.serverboiUtilsLayer],
      environment: {
        //Add workflow table
        TOKEN_BUCKET: props.tokenBucket.bucketName,
        USER_TABLE: props.userList.tableName,
        SERVER_TABLE: props.serverList.tableName,
      },
    });
    provision.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "sts:AssumeRole",
        ],
      })
    );

    const putTokenName = "Put-Token-Lambda";
    const putToken = new PythonLambda(this, putTokenName, {
      name: putTokenName,
      codePath: "lambdas/handlers/provision_workflow/put_token/",
      handler: "put_token.main.lambda_handler",
      environment: {
        //Add workflow table
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

    const finishProvisionName = "Finish-Provision-Lambda";
    const finishProvision = new PythonLambda(this, finishProvisionName, {
      name: finishProvisionName,
      codePath:
        "lambdas/handlers/provision_workflow/finish_provision_workflow/",
      handler: "finish_provision_workflow.main.lambda_handler",
      environment: {
        DISCORD_TOKEN: disordToken.secretValue.toString(),
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

    //step definitions
    const provisionStep = new LambdaInvoke(this, "Provision-Step", {
      lambdaFunction: provision.lambda,
      outputPath: "$.Payload",
    });

    const tokenNodeNames = ["Wait-For-Download", "Starting-Server-Client"];

    var tokenNodes = new Array<LambdaInvoke>();

    tokenNodeNames.forEach((stageName) => {
      var stage = new LambdaInvoke(this, stageName, {
        lambdaFunction: putToken.lambda,
        inputPath: "$",
        integrationPattern: IntegrationPattern.WAIT_FOR_TASK_TOKEN,
        timeout: Duration.hours(1),
        payload: {
          type: InputType.OBJECT,
          value: {
            "Input.$": "$",
            TaskToken: JsonPath.taskToken,
          },
        },
      });

      tokenNodes.push(stage);
    });

    const finishProvisionStep = new LambdaInvoke(
      this,
      "Finish-Provision-Step",
      {
        lambdaFunction: finishProvision.lambda,
        outputPath: "$.Payload",
      }
    );

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
