import { Construct } from "monocdk";
import { LayerVersion } from "monocdk/aws-lambda";
import {
  StateMachine,
  Succeed,
} from "monocdk/aws-stepfunctions";
import { LambdaInvoke } from "monocdk/aws-stepfunctions-tasks";
import { PolicyStatement } from "monocdk/aws-iam";
import { Table } from "monocdk/aws-dynamodb";
import { GoLambda } from "../GoLambdaConstruct";
import { 
  TerminateServer
 } from "../../../function_uri_list.json"

export interface TerminateServerProps {
  readonly serverList: Table;
  readonly ownerList: Table;
  readonly keyBucket: string;
  readonly discordToken: string;
}

export class TerminateServerWorkflow extends Construct {
  public readonly terminationStateMachine: StateMachine;

  constructor(scope: Construct, id: string, props: TerminateServerProps) {
    super(scope, id);

    const terminateName = "Terminate-Lambda-Go";
    const terminate = new GoLambda(this, terminateName, {
      name: terminateName,
      bucket: TerminateServer.bucket,
      object: TerminateServer.key,
      environment: {
        OWNER_TABLE: props.ownerList.tableName,
        SERVER_TABLE: props.serverList.tableName,
        DISCORD_TOKEN: props.discordToken,
        KEY_BUCKET: props.keyBucket,
        STAGE: "Prod"
      },
    });
    terminate.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "s3:DeleteObject",
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "sts:AssumeRole",
        ],
      })
    );

    //Step definitions
    const terminateLambdaStep = new LambdaInvoke(this, "Terminate-Step", {
      lambdaFunction: terminate.lambda,
    });


    const termStepDefinition = terminateLambdaStep;

    this.terminationStateMachine = new StateMachine(
      this,
      "Terminate-Server-State-Machine",
      {
        definition: termStepDefinition,
        stateMachineName: "Terminate-Server-Workflow",
      }
    );
  }
}
