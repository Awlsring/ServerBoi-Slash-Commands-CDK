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

    const serverBoiUtils = new LayerVersion(
      this,
      "Serverboi-Utils-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/serverboi_utils/serverboi_utils.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for ServerBoi Utils",
        layerVersionName: "ServerBoi-Utils-Layer"
      }
    )

    const verifyName = "ServerBoi-Verify-And-Provision-Lambda";
    const verifyLambda = new Function(this, verifyName, {
      runtime: Runtime.PYTHON_3_8,
      handler: "verify_and_provision.main.lambda_handler",
      code: Code.fromAsset("lambdas/handlers/verify_and_provision_lambda/"),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      layers: [props.resourcesStack.discordLayer, serverBoiUtils],
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

    const checkName = "ServerBoi-Check-Server-Status-Lambda";
    const checkLambda = new Function(this, checkName, {
      runtime: Runtime.PYTHON_3_8,
      handler: "check_server_status.main.lambda_handler",
      code: Code.fromAsset("lambdas/handlers/check_server_status/"),
      memorySize: 128,
      layers: [props.resourcesStack.a2sLayer, props.resourcesStack.discordLayer, serverBoiUtils],
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      functionName: checkName,
      environment: {
        USER_TABLE: props.resourcesStack.userList.tableName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
      },
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
          "dynamodb:DeleteItem",
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
        outputPath: '$.Payload'
      }
    );

    const waitForProvision = new Wait(this, 'Wait-For-Provision', {
      time: WaitTime.secondsPath('$.wait_time'),
    })

    const checkServerStatus = new LambdaInvoke(
      this,
      "Check-Server-Status-Step",
      {
        lambdaFunction: checkLambda,
        inputPath: "$."
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

    const terminateName = "ServerBoi-Verify-And-Terminate-Lambda";
    const terminateLambda = new Function(this, terminateName, {
      runtime: Runtime.PYTHON_3_8,
      handler: "terminate_lambda.main.lambda_handler",
      code: Code.fromAsset("lambdas/handlers/terminate_lambda/"),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      layers: [props.resourcesStack.discordLayer, serverBoiUtils],
      functionName: terminateName,
      environment: {
        RESOURCES_BUCKET: props.resourcesStack.resourcesBucket.bucketName,
        USER_TABLE: props.resourcesStack.userList.tableName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
      },
      role: new Role(this, `${terminateName}-Role`, {
        assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
        roleName: `${terminateName}-Role`,
      }),
    });

    terminateLambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "sts:AssumeRole",
          "ec2:TerminateInstances"
        ],
      })
    );

    //step definitions
    const terminateLambdaStep = new LambdaInvoke(
      this,
      "Terminate-Step",
      {
        lambdaFunction: terminateLambda,
      }
    );

    const termEndStep = new Succeed(this, 'Term-End-Step')

    const termStepDefinition = terminateLambdaStep.next(termEndStep)

    const terminate = new StateMachine(this, "Terminate-Server-State-Machine", {
      definition: termStepDefinition,
      stateMachineName: "Terminate-Server-Workflow",
    });

  }
}
