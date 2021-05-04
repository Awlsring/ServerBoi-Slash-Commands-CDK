import { Construct, Stage, StageProps } from "monocdk";
import { ApiGatewayStack } from "../ApiGatewayStack";
import { ServerlessBoiResourcesStack } from "../ServerlessBoiResourcesStack";
import { ServerWorkflowsStack } from "../ServerWorkflowsStack";

export class PipelineStage extends Stage {
  constructor(scope: Construct, id: string, props?: StageProps) {
    super(scope, id, props);

    const resourcesStack = new ServerlessBoiResourcesStack(
      this,
      "Resources-Stack"
    );
    new ApiGatewayStack(this, "Api-Gateway-Stack", {
      resourcesStack: resourcesStack,
    });
    new ServerWorkflowsStack(this, "Workflows-Stack", {
      resourcesStack: resourcesStack,
    });
  }
}
