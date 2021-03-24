#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { ServerlessBoiStack } from '../lib/serverless_boi-stack';

const app = new cdk.App();
new ServerlessBoiStack(app, 'ServerlessBoiStack');
