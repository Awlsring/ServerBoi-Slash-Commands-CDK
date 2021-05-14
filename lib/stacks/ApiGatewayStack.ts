import { Stack, StackProps, Construct, Duration } from "monocdk";
import {
  RestApi,
  LambdaIntegration,
  PassthroughBehavior,
} from "monocdk/aws-apigateway";
import {
  Function,
  Runtime,
  Tracing,
  Code,
  LayerVersion,
} from "monocdk/aws-lambda";
import { Role, ServicePrincipal, PolicyStatement } from "monocdk/aws-iam";
import { ServerlessBoiResourcesStack } from "./ServerlessBoiResourcesStack";
import { Secret } from "monocdk/aws-secretsmanager"
import { PythonLambda } from "../constructs/PythonLambdaConstruct";

export interface ApiGatewayStackProps extends StackProps {
  readonly resourcesStack: ServerlessBoiResourcesStack;
}

export class ApiGatewayStack extends Stack {
  //Creates all resources needed for the API Gateway
  constructor(scope: Construct, id: string, props: ApiGatewayStackProps) {
    super(scope, id, props);

    const publicKey = Secret.fromSecretCompleteArn(
      this,
      'ServerBoi-Key',
      'arn:aws:secretsmanager:us-west-2:742762521158:secret:ServerBoi-Public-Key-gB6pgg'
    )

    const api = new RestApi(this, "ServerlessBoi-Discord-Endpoint");

    const url = api.url

    const applicationId = process.env["PUBLIC_ID"];
    console.log(applicationId);

    const flaskLayer = new LayerVersion(
      this,
      "ServerlessBoi-Discord-Interactions-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/discordInteractions/discordIntegrationsLayer.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for Discord Interactions",
        layerVersionName: "ServerlessBoi-Discord-Interactions-Layer",
      }
    );

    const serverBoiUtils = new LayerVersion(
      this,
      "Serverboi-Utils-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/serverboi_utils/serverboi_utils.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for ServerBoi Utils",
        layerVersionName: "ServerBoi-Utils-Layer"
      }
    )

    const lambdaLayers = [
      flaskLayer,
      props.resourcesStack.a2sLayer,
      props.resourcesStack.discordLayer,
      props.resourcesStack.requestsLayer,
      serverBoiUtils
    ]

    const commandHandler = new PythonLambda(this, "Command-Handler", {
      name: "Command-Handler",
      codePath: "lambdas/handlers/interactions/",
      handler: "serverboi_interactions_lambda.main.lambda_handler",
      layers: lambdaLayers,
      environment: {
        PUBLIC_KEY: publicKey.secretValue.toString(),
        RESOURCES_BUCKET: props.resourcesStack.resourcesBucket.bucketName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
        USER_TABLE: props.resourcesStack.userList.tableName,
        PROVISION_ARN: 'arn:aws:states:us-west-2:742762521158:stateMachine:Provision-Server-Workflow',
        TERMINATE_ARN: 'arn:aws:states:us-west-2:742762521158:stateMachine:Terminate-Server-Workflow'
      },
    })
    commandHandler.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "dynamodb:Scan",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "states:StartExecution",
          "dynamodb:GetItem",
          "sts:AssumeRole",
        ],
      })
    );

    const bootstrapCall = new PythonLambda(this, "Bootstrap-Call", {
      name: "Bootstrap-Call",
      codePath: "lambdas/handlers/bootstrap_call/",
      handler: "bootstrap_call.main.lambda_handler",
      layers: lambdaLayers,
      environment: {
        API_URL: url,
        PUBLIC_KEY: publicKey.secretValue.toString(),
        RESOURCES_BUCKET: props.resourcesStack.resourcesBucket.bucketName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
        USER_TABLE: props.resourcesStack.userList.tableName,
        PROVISION_ARN: 'arn:aws:states:us-west-2:742762521158:stateMachine:Provision-Server-Workflow',
        TERMINATE_ARN: 'arn:aws:states:us-west-2:742762521158:stateMachine:Terminate-Server-Workflow'
      },
    })
    bootstrapCall.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "states:SendTaskSuccess"
        ],
      })
    );

    
    
    const bootstrap = api.root.addResource("bootstrap")
    
    bootstrap.addMethod(
      "Post",
      new LambdaIntegration(bootstrapCall.lambda, {
        proxy: false,
        passthroughBehavior: PassthroughBehavior.NEVER,
        requestTemplates: {
            'application/json': `{ 
                "token": "$input.params('token')"
            }`,
        },
        integrationResponses: [{
            statusCode: '200',
            responseParameters: {
                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET'",
                "method.response.header.Access-Control-Allow-Origin": "'*'"
              },
        }]}), {
        methodResponses: [{ 
            statusCode: '200',
            responseParameters: {
                'method.response.header.Access-Control-Allow-Headers': true,
                'method.response.header.Access-Control-Allow-Methods': true,
                'method.response.header.Access-Control-Allow-Credentials': true,
                'method.response.header.Access-Control-Allow-Origin': true,
            },
        }]
    })

    const discord = api.root.addResource("discord");

    discord.addMethod(
      "Post",
      new LambdaIntegration(commandHandler.lambda, {
        proxy: true,
        passthroughBehavior: PassthroughBehavior.NEVER,
        requestTemplates: {
          "application/json": `{
          "method": "$context.httpMethod",
          "body" : $input.json("$"),
          "headers": {
              #foreach($param in $input.params().header.keySet())
              "$param": "$util.escapeJavaScript($input.params().header.get($param))"
              #if($foreach.hasNext),#end
              #end
          }
        }`,
        },
      })
    );
  }
}
