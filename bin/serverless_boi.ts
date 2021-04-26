#!/usr/bin/env node
import { App } from "monocdk";
import { ApiGatewayStack } from "../lib/stacks/ApiGatewayStack";
import { ServerlessBoiResourcesStack } from "../lib/stacks/ServerlessBoiResourcesStack";
import { PipelineStack } from "../lib/stacks/PipelineStack";

const app = new App();
const pipeline = new PipelineStack(app, "ServerlessBoi-Pipeline");
const resourcesStack = new ServerlessBoiResourcesStack(
  app,
  "ServerlessBoi-Resources-Stack"
);
new ApiGatewayStack(app, "ServerlessBoi-Api-Gateway-Stack", {
  resourcesStack: resourcesStack,
});
