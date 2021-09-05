import { Stack, StackProps, Construct, Token } from "monocdk";
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

    const bootstrapConstruct = new WaitForBootstrap(
      this,
      "Wait-For-Bootstrap-Construct"
    );

    const provisionWorkflow = new ProvisionServerWorkflow(
      this,
      "Provision-Workflow",
      {
        serverList: props.resourcesStack.serverList,
        userList: props.resourcesStack.userList,
        tokenBucket: props.resourcesStack.tokenBucket,
        tokenQueue: bootstrapConstruct.tokenQueue,
        awsTable: props.resourcesStack.awsTable,
        linodeTable: props.resourcesStack.linodeTable,
        webhookList: props.resourcesStack.webhookList,
        channelList: props.resourcesStack.channelTable,
      }
    );

    this.provisionStateMachineArn =
      provisionWorkflow.provisionStateMachine.stateMachineArn;

    const terminationWorkflow = new TerminateServerWorkflow(
      this,
      "Terminate-Workflow",
      {
        serverList: props.resourcesStack.serverList,
        userList: props.resourcesStack.userList,
      }
    );

    this.terminationStateMachineArn =
      terminationWorkflow.terminationStateMachine.stateMachineArn;
  }
}
