import { Stack, Construct, RemovalPolicy } from "monocdk";
import { Table, AttributeType, Attribute } from "monocdk/aws-dynamodb";
import { Bucket } from "monocdk/aws-s3";
import { BucketDeployment, Source } from "monocdk/aws-s3-deployment";
import {
  Runtime,
  Code,
  LayerVersion,
} from "monocdk/aws-lambda";

export class ServerlessBoiResourcesStack extends Stack {
  //Creates all resources referenced across stacks

  readonly resourcesBucket: Bucket;
  readonly serverList: Table;
  readonly userList: Table;
  readonly discordLayer: LayerVersion
  readonly requestsLayer: LayerVersion
  readonly a2sLayer: LayerVersion
  readonly serverBoiUtils: LayerVersion


  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.discordLayer = new LayerVersion(
      this,
      "ServerBoi-Discord-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/discordpy/discordpy.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for Discord.py",
        layerVersionName: "ServerBoi-Discord-Layer",
        removalPolicy: RemovalPolicy.RETAIN
      }
    );

    this.serverBoiUtils = new LayerVersion(
      this,
      "Serverboi-Utils-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/serverboi_utils/serverboi_utils.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for ServerBoi Utils",
        layerVersionName: "ServerBoi-Utils-Layer",
        removalPolicy: RemovalPolicy.RETAIN
      }
    )

    this.requestsLayer = new LayerVersion(
      this,
      "ServerBoi-Request-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/requests/requests.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for Requests",
        layerVersionName: "ServerBoi-Requests-Layer",
        removalPolicy: RemovalPolicy.RETAIN
      }
    );

    this.a2sLayer = new LayerVersion(
      this,
      "ServerBoi-A2S-Layer",
      {
        code: Code.fromAsset(
          "lambdas/layers/a2s/a2s.zip"
        ),
        compatibleRuntimes: [Runtime.PYTHON_3_8],
        description: "Lambda Layer for A2S",
        layerVersionName: "ServerBoi-A2S-Layer",
        removalPolicy: RemovalPolicy.RETAIN
      }
    );

    this.resourcesBucket = new Bucket(this, "Resources-Bucket", {
      bucketName: "serverboi-resources-bucket",
      publicReadAccess: true,
    });

    const deployment = new BucketDeployment(this, "Bucket-Deployment", {
      sources: [Source.asset("lib/stacks/resources/onboardingDeployment")],
      destinationBucket: this.resourcesBucket,
    });

    this.serverList = new Table(this, "Server-Table", {
      partitionKey: { name: "ServerID", type: AttributeType.STRING },
      tableName: "ServerBoi-Server-List",
    });

    this.userList = new Table(this, "User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "ServerBoi-User-List",
    });
  }
}
