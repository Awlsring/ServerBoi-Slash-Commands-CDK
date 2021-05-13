import { Construct, Duration } from "monocdk";
import { LayerVersion } from "monocdk/aws-lambda";
import {
  StateMachine,
  Choice,
  Condition,
  Wait,
  WaitTime,
  Succeed,
  Fail,
  InputType
} from "monocdk/aws-stepfunctions";
import { LambdaInvoke, SqsSendMessage } from "monocdk/aws-stepfunctions-tasks";
import { PolicyStatement } from "monocdk/aws-iam";
import { Table } from "monocdk/aws-dynamodb";
import { PythonLambda } from "../PythonLambdaConstruct"

export interface TerminateServerProps {
  readonly discordLayer: LayerVersion
  readonly serverboiUtilsLayer: LayerVersion
  readonly serverList: Table
  readonly userList: Table
}

export class TerminateServerWorkflow extends Construct {

  public readonly terminationWorkflow: StateMachine

  constructor(scope: Construct, id: string, props: TerminateServerProps) {
    super(scope, id);

    const terminateName = "ServerBoi-Verify-And-Terminate-Lambda";

    const terminate = new PythonLambda(this, terminateName, {
      name: terminateName,
      codePath: "lambdas/handlers/terminate_lambda/",
      handler: "terminate_lambda.main.lambda_handler",
      layers: [props.discordLayer, props.serverboiUtilsLayer],
      environment:{
          USER_TABLE: props.userList.tableName,
          SERVER_TABLE: props.serverList.tableName,
      },
    })

    terminate.lambda.addToRolePolicy(
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
        lambdaFunction: terminate.lambda,
      }
    );

    const termEndStep = new Succeed(this, 'Term-End-Step')

    const termStepDefinition = terminateLambdaStep.next(termEndStep)

    this.terminationWorkflow = new StateMachine(this, "Terminate-Server-State-Machine", {
      definition: termStepDefinition,
      stateMachineName: "Terminate-Server-Workflow",
    });
    

  }
}