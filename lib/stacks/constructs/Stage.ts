import { Construct, Stage, StageProps } from "monocdk";
import { ApiGatewayStack } from "../ApiGatewayStack";
import { ServerlessBoiResourcesStack } from "../ServerlessBoiResourcesStack";

export class PipelineStage extends Stage {
  constructor(scope: Construct, id: string, props?: StageProps) {
    super(scope, id, props);

    const resourcesStack = new ServerlessBoiResourcesStack(
      this,
      "ServerlessBoi-Resources-Stack"
    );
    new ApiGatewayStack(this, "ServerlessBoi-Api-Gateway-Stack", {
      resourcesStack: resourcesStack,
    });
  }
}
