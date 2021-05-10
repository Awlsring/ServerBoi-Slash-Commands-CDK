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

    const lambdaLayers = [
      flaskLayer,
      props.resourcesStack.a2sLayer,
      props.resourcesStack.discordLayer,
      props.resourcesStack.requestsLayer,
      props.resourcesStack.serverBoiUtils
    ]
    const lambda = new Function(this, "ServerlessBoi-Main-Lambda", {
      runtime: Runtime.PYTHON_3_8,
      handler: "serverboi_interactions_lambda.main.lambda_handler",
      code: Code.fromAsset("lambdas/handlers/interactions/"),
      layers: lambdaLayers,
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      functionName: "ServerlessBoi-Main-Lambda",
      environment: {
        PUBLIC_KEY: publicKey.secretValue.toString(),
        RESOURCES_BUCKET: props.resourcesStack.resourcesBucket.bucketName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
        USER_TABLE: props.resourcesStack.userList.tableName,
        PROVISION_ARN: 'arn:aws:states:us-west-2:742762521158:stateMachine:Provision-Server-Workflow'
      },
      role: new Role(this, "ServerlessBoi-Main-Lambda-Role", {
        assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
        roleName: "ServerlessBoi-Main-Lambda-Role",
      }),
    });

    lambda.addToRolePolicy(
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

    const api = new RestApi(this, "ServerlessBoi-Discord-Endpoint");

    const discord = api.root.addResource("discord");

    discord.addMethod(
      "Post",
      new LambdaIntegration(lambda, {
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
