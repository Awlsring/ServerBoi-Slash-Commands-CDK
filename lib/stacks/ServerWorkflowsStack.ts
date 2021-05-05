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

    //step definitions
    const verifyLambdaStep = new LambdaInvoke(
      this,
      "Verify-And-Provision-Step",
      {
        lambdaFunction: verifyLambda,
      }
    );

    const checkServerStatus = new Pass(this, "Check-Server-Status-Step");

    const stepDefinition = verifyLambdaStep.next(checkServerStatus);

    new StateMachine(this, "Provision-Server-State-Machine", {
      definition: stepDefinition,
      stateMachineName: "Provision-Server-Workflow",
    });
  }
}
