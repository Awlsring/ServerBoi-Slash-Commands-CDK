#!/usr/bin/env node
import { App } from "monocdk";
import { ApiGatewayStack } from "../lib/stacks/ApiGatewayStack";
import { ServerlessBoiResourcesStack } from "../lib/stacks/ServerlessBoiResourcesStack";
import { ServerWorkflowsStack } from "../lib/stacks/ServerWorkflowsStack";

const app = new App();

const resourcesStack = new ServerlessBoiResourcesStack(app, "Resources-Stack");

const workflowStack = new ServerWorkflowsStack(app, "Workflows-Stack", {
  resourcesStack: resourcesStack,
});

new ApiGatewayStack(app, "Api-Gateway-Stack", {
  resourcesStack: resourcesStack,
  workflowStack: workflowStack,
});
