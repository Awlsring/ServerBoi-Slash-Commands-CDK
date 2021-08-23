import { Stack, Construct, RemovalPolicy, Duration } from "monocdk";
import { Table, AttributeType } from "monocdk/aws-dynamodb";
import { Bucket } from "monocdk/aws-s3";
import { BucketDeployment, Source } from "monocdk/aws-s3-deployment";
import { Runtime, Code, LayerVersion } from "monocdk/aws-lambda";

export class ServerlessBoiResourcesStack extends Stack {
  //Creates all resources referenced across stacks
  readonly resourcesBucket: Bucket;
  readonly clientBucket: Bucket;
  readonly tokenBucket: Bucket;
  readonly webhookList: Table;
  readonly serverList: Table;
  readonly userList: Table;
  readonly awsTable: Table;
  readonly linodeTable: Table;
  readonly requestsLayer: LayerVersion;
  readonly a2sLayer: LayerVersion;
  readonly serverBoiUtils: LayerVersion;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.requestsLayer = new LayerVersion(this, "ServerBoi-Request-Layer", {
      code: Code.fromAsset("lambdas/layers/requests/requests.zip"),
      compatibleRuntimes: [Runtime.PYTHON_3_8],
      description: "Lambda Layer for Requests",
      layerVersionName: "ServerBoi-Requests-Layer",
      removalPolicy: RemovalPolicy.RETAIN,
    });

    this.a2sLayer = new LayerVersion(this, "ServerBoi-A2S-Layer", {
      code: Code.fromAsset("lambdas/layers/a2s/a2s.zip"),
      compatibleRuntimes: [Runtime.PYTHON_3_8],
      description: "Lambda Layer for A2S",
      layerVersionName: "ServerBoi-A2S-Layer",
      removalPolicy: RemovalPolicy.RETAIN,
    });

    this.resourcesBucket = new Bucket(this, "Resources-Bucket", {
      bucketName: "serverboi-resources-bucket",
      removalPolicy: RemovalPolicy.DESTROY,
      publicReadAccess: true,
    });

    this.clientBucket = new Bucket(this, "Client-Bucket", {
      bucketName: "serverboi-client-bucket",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.tokenBucket = new Bucket(this, "Token-Bucket", {
      bucketName: "serverboi-server-provision-token-bucket",
      publicReadAccess: true,
      autoDeleteObjects: true,
      removalPolicy: RemovalPolicy.DESTROY,
      lifecycleRules: [
        {
          expiration: Duration.days(1),
        },
      ],
    });

    const deployment = new BucketDeployment(this, "Bucket-Deployment", {
      sources: [Source.asset("lib/stacks/resources/onboardingDeployment")],
      destinationBucket: this.resourcesBucket,
    });

    this.webhookList = new Table(this, "Webhook-Table", {
      partitionKey: { name: "GuildID", type: AttributeType.STRING },
      tableName: "ServerBoi-Webhook-List",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.serverList = new Table(this, "Server-Table", {
      partitionKey: { name: "ServerID", type: AttributeType.STRING },
      tableName: "ServerBoi-Server-List",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.linodeTable = new Table(this, "Linode-User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "Linode-User-List",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.awsTable = new Table(this, "AWS-User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "AWS-User-List",
      removalPolicy: RemovalPolicy.DESTROY,
    });

    this.userList = new Table(this, "User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "ServerBoi-User-List",
      removalPolicy: RemovalPolicy.DESTROY,
    });
  }
}
