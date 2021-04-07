#!/usr/bin/env node
import { App } from "monocdk";
import { ApiGatewayStack } from "../lib/stacks/ApiGatewayStack";
import { ServerlessBoiResourcesStack } from "../lib/stacks/ServerlessBoiResourcesStack";

const app = new App();
new ServerlessBoiResourcesStack(app, "ServerlessBoi-Resources-Stack");
new ApiGatewayStack(app, "ServerlessBoi-Api-Gateway-Stack");
