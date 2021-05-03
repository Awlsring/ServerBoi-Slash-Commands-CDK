#!/usr/bin/env node
import { App } from "monocdk";
import { PipelineStack } from "../lib/stacks/PipelineStack";

const app = new App();
const pipeline = new PipelineStack(app, "ServerlessBoi-Pipeline");
