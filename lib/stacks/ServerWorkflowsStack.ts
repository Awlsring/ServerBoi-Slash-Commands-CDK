import { Stack, StackProps, Construct, Token } from "monocdk";
import { Runtime, Code, LayerVersion } from "monocdk/aws-lambda";
import { ServerlessBoiResourcesStack } from "./ServerlessBoiResourcesStack";
import { WaitForBootstrap } from "../constructs/WaitForBootstrap";
import { ProvisionServerWorkflow } from "../constructs/workflows/ProvisionServerWorkflow";
import { TerminateServerWorkflow } from "../constructs/workflows/TerminateServerWorkflow";

export interface ServerWorkflowsStackProps extends StackProps {
  readonly resourcesStack: ServerlessBoiResourcesStack;
}

export class ServerWorkflowsStack extends Stack {
  readonly provisionStateMachineArn: string;
  readonly terminationStateMachineArn: string;

  constructor(scope: Construct, id: string, props: ServerWorkflowsStackProps) {
    super(scope, id, props);
    const serverBoiUtils = new LayerVersion(this, "Serverboi-Util-Layer", {
      code: Code.fromAsset(
        "lambdas/layers/serverboi_utils/serverboi_utils.zip"
      ),
      compatibleRuntimes: [Runtime.PYTHON_3_8],
      description: "Lambda Layer for ServerBoi Util",
      layerVersionName: "ServerBoi-Util-Layer",
    });

    const cloudApis = new LayerVersion(this, "Cloud-Api-Layer", {
      code: Code.fromAsset("lambdas/layers/cloud_apis/cloud_apis.zip"),
      compatibleRuntimes: [Runtime.PYTHON_3_8],
      description: "Lambda Layer for Cloud Provider APIs",
      layerVersionName: "Cloud-Api-Layer",
    });

    const discordLayer = new LayerVersion(this, "discordpy-Layer", {
      code: Code.fromAsset("lambdas/layers/discordpy/discordpy.zip"),
      compatibleRuntimes: [Runtime.PYTHON_3_8],
      description: "Lambda Layer for Discordpy",
      layerVersionName: "Discordpy-Layer",
    });

    const bootstrapConstruct = new WaitForBootstrap(
      this,
      "Wait-For-Bootstrap-Construct"
    );

    const provisionWorkflow = new ProvisionServerWorkflow(
      this,
      "Provision-Workflow",
      {
        discordLayer: discordLayer,
        serverboiUtilsLayer: serverBoiUtils,
        serverList: props.resourcesStack.serverList,
        userList: props.resourcesStack.userList,
        tokenBucket: props.resourcesStack.tokenBucket,
        tokenQueue: bootstrapConstruct.tokenQueue,
        awsTable: props.resourcesStack.awsTable,
        linodeTable: props.resourcesStack.linodeTable,
        cloudApis: cloudApis,
      }
    );

    this.provisionStateMachineArn =
      provisionWorkflow.provisionStateMachine.stateMachineArn;

    const terminationWorkflow = new TerminateServerWorkflow(
      this,
      "Terminate-Workflow",
      {
        discordLayer: discordLayer,
        serverboiUtilsLayer: serverBoiUtils,
        serverList: props.resourcesStack.serverList,
        userList: props.resourcesStack.userList,
      }
    );

    this.terminationStateMachineArn =
      terminationWorkflow.terminationStateMachine.stateMachineArn;
  }
}
