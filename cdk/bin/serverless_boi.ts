#!/usr/bin/env node
import { App } from 'monocdk';
import { ServerlessBoiStack } from '../lib/stacks/serverless_boi-stack';

const app = new App();
new ServerlessBoiStack(app, 'ServerlessBoiStack');
