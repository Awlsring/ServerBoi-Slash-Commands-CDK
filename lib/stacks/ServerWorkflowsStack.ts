import { Stack, StackProps, Construct, Token } from "monocdk";
import { ServerlessBoiResourcesStack } from "./ResourcesStack";
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

    const terminationWorkflow = new TerminateServerWorkflow(
      this,
      "Terminate-Workflow",
      {
        serverList: props.resourcesStack.serverList,
        ownerList: props.resourcesStack.ownerList,
      }
    );

    this.terminationStateMachineArn = terminationWorkflow.terminationStateMachine.stateMachineArn;
    
    const provisionWorkflow = new ProvisionServerWorkflow(
      this,
      "Provision-Workflow",
      {
        serverList: props.resourcesStack.serverList,
        ownerList: props.resourcesStack.ownerList,
        tokenBucket: props.resourcesStack.tokenBucket,
        tokenQueue: bootstrapConstruct.tokenQueue,
        webhookList: props.resourcesStack.webhookList,
        channelList: props.resourcesStack.channelTable,
        discordToken: props.resourcesStack.discordToken,
        terminationWorkflow: terminationWorkflow.terminationStateMachine,
        provisionConfigurationBucket: props.resourcesStack.provisionConfigBucket,
        dockerComposeTemplateBucket: props.resourcesStack.dockerComposeBucket,
        sshBucket: props.resourcesStack.sshBucket,
      }
    );

    this.provisionStateMachineArn =
      provisionWorkflow.provisionStateMachine.stateMachineArn;

  }
}
