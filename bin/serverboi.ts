#!/usr/bin/env node
import { App } from "monocdk";
import { ApiGatewayStack } from "../lib/stacks/ApiGatewayStack";
import { EmbedManagerStack } from "../lib/stacks/EmbedManagerStack";
import { ServerlessBoiResourcesStack } from "../lib/stacks/ResourcesStack";
import { ServerWorkflowsStack } from "../lib/stacks/ServerWorkflowsStack";

const app = new App();

const resourcesStack = new ServerlessBoiResourcesStack(app, "Resources-Stack");

const workflowStack = new ServerWorkflowsStack(app, "Workflows-Stack", {
  resourcesStack: resourcesStack,
});

const embedManagerStack = new EmbedManagerStack(app, "Embed-Manager-Stack",{
  serverList: resourcesStack.serverList,
  discordToken: resourcesStack.discordToken
})

new ApiGatewayStack(app, "Api-Gateway-Stack", {
  resourcesStack: resourcesStack,
  workflowStack: workflowStack,
});
