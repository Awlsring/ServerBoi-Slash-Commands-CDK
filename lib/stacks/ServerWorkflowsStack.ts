import { Stack, StackProps, Construct, Duration } from "monocdk";
import {
  Function,
  Runtime,
  Tracing,
  Code,
  LayerVersion,
} from "monocdk/aws-lambda";
import {
  StateMachine,
  Choice,
  Condition,
  Pass,
  Wait,
  WaitTime,
  Succeed,
  Fail
} from "monocdk/aws-stepfunctions";
import { LambdaInvoke } from "monocdk/aws-stepfunctions-tasks";
import { PolicyStatement, Role, ServicePrincipal } from "monocdk/aws-iam";
import { ServerlessBoiResourcesStack } from "./ServerlessBoiResourcesStack";

export interface ServerWorkflowsStackProps extends StackProps {
  readonly resourcesStack: ServerlessBoiResourcesStack;
}

export class ServerWorkflowsStack extends Stack {
  //Creates all resources needed for the API Gateway
  constructor(scope: Construct, id: string, props: ServerWorkflowsStackProps) {
    super(scope, id, props);

    const verifyName = "ServerBoi-Verify-And-Provision-Lambda";
    const verifyLambda = new Function(this, verifyName, {
      runtime: Runtime.PYTHON_3_8,
      handler: "verify_and_provision.main.lambda_handler",
      code: Code.fromAsset("lambdas/handlers/verify_and_provision_lambda/"),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      functionName: verifyName,
      environment: {
        RESOURCES_BUCKET: props.resourcesStack.resourcesBucket.bucketName,
        USER_TABLE: props.resourcesStack.userList.tableName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
      },
      role: new Role(this, `${verifyName}-Role`, {
        assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
        roleName: `${verifyName}-Role`,
      }),
    });

    const a2sLayer = new LayerVersion(
      this,
      "A2S-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/a2s/a2s.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for A2S",
        layerVersionName: "ServerlessBoi-A2S-Layer",
      }
    );

    const checkName = "ServerBoi-Check-Server-Status-Lambda";
    const checkLambda = new Function(this, checkName, {
      runtime: Runtime.PYTHON_3_8,
      handler: "check_server_status.main.lambda_handler",
      code: Code.fromAsset("lambdas/handlers/check_server_status/"),
      memorySize: 128,
      layers: [a2sLayer],
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      functionName: checkName,
      role: new Role(this, `${checkName}-Role`, {
        assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
        roleName: `${checkName}-Role`,
      }),
    });

    verifyLambda.addToRolePolicy(
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

    checkLambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "ec2:TerminateInstances",
          "sts:AssumeRole",
        ],
      })
    );

    //step definitions
    const verifyLambdaStep = new LambdaInvoke(
      this,
      "Verify-And-Provision-Step",
      {
        lambdaFunction: verifyLambda,
      }
    );

    const waitForProvision = new Wait(this, 'Wait-For-Provision', {
      time: WaitTime.secondsPath('$.Payload.wait_time'),
    })

    const checkServerStatus = new LambdaInvoke(
      this,
      "Check-Server-Status-Step",
      {
        lambdaFunction: checkLambda,
        inputPath: "$.Payload"
      });

    const isServerUpCheck = new Choice(this, 'Is-Server-Up-Check', {
      inputPath:"$.Payload"
    })

    const errorStep = new Fail(this, 'Fail-Step')

    const endStep = new Succeed(this, 'End-Step')

    const stepDefinition = verifyLambdaStep
      .next(waitForProvision)
      .next(checkServerStatus)
      .next(isServerUpCheck)
      isServerUpCheck.when(Condition.booleanEquals('$.rollback', true), errorStep) 
      isServerUpCheck.when(Condition.booleanEquals('$.server_up', false), waitForProvision);
      isServerUpCheck.when(Condition.booleanEquals('$.server_up', true), endStep);

    const provision = new StateMachine(this, "Provision-Server-State-Machine", {
      definition: stepDefinition,
      stateMachineName: "Provision-Server-Workflow",
    });
  }
}
