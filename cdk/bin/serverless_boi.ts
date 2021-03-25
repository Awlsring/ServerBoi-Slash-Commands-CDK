#!/usr/bin/env node
import { App } from 'monocdk';
import { ApiGatewayStack } from '../lib/stacks/ApiGatewayStack';

const app = new App();
new ApiGatewayStack(app, 'ServerlessBoiStack');
