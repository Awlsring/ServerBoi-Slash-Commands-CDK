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
import { config } from "dotenv";

export interface ApiGatewayStackProps extends StackProps {
  readonly resourcesStack: ServerlessBoiResourcesStack;
}

export class ApiGatewayStack extends Stack {
  //Creates all resources needed for the API Gateway
  constructor(scope: Construct, id: string, props: ApiGatewayStackProps) {
    super(scope, id, props);

    config({
      path: "../../.env",
    });

    const applicationId = process.env["APPLICATION_ID"];

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

    const lambda = new Function(this, "ServerlessBoi-Main-Lambda", {
      runtime: Runtime.PYTHON_3_8,
      handler: "main.lambda_handler",
      code: Code.fromAsset(
        "lambdas/handlers/interactions/serverboi_interactions_lambda"
      ),
      layers: [flaskLayer],
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(60),
      functionName: "ServerlessBoi-Main-Lambda",
      environment: {
        APPLICATION_ID: <string>applicationId,
        RESOURCES_BUCKET: props.resourcesStack.resourcesBucket.bucketName,
        SERVER_TABLE: props.resourcesStack.serverList.tableName,
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
