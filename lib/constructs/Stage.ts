import { Construct, Stage, StageProps } from "monocdk";
import { ApiGatewayStack } from "../stacks/ApiGatewayStack";
import { ServerlessBoiResourcesStack } from "../stacks/ServerlessBoiResourcesStack";
import { ServerWorkflowsStack } from "../stacks/ServerWorkflowsStack";

export class PipelineStage extends Stage {
  constructor(scope: Construct, id: string, props?: StageProps) {
    super(scope, id, props);

    const resourcesStack = new ServerlessBoiResourcesStack(
      this,
      "Resources-Stack"
    );
    const workflowStack = new ServerWorkflowsStack(this, "Workflows-Stack", {
      resourcesStack: resourcesStack,
    });
    new ApiGatewayStack(this, "Api-Gateway-Stack", {
      workflowStack: workflowStack,
      resourcesStack: resourcesStack,
    });
  }
}
