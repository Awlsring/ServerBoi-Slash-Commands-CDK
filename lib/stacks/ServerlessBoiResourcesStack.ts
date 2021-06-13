import { Stack, Construct, RemovalPolicy } from "monocdk";
import { Table, AttributeType, Attribute } from "monocdk/aws-dynamodb";
import { Bucket } from "monocdk/aws-s3";
import { BucketDeployment, Source } from "monocdk/aws-s3-deployment";
import { Runtime, Code, LayerVersion } from "monocdk/aws-lambda";

export class ServerlessBoiResourcesStack extends Stack {
  //Creates all resources referenced across stacks

  readonly resourcesBucket: Bucket;
  readonly clientBucket: Bucket;
  readonly serverList: Table;
  readonly userList: Table;
  readonly awsTable: Table;
  readonly linodeTable: Table;
  readonly discordLayer: LayerVersion;
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
      publicReadAccess: true,
    });

    this.clientBucket = new Bucket(this, "Client-Bucket", {
      bucketName: "serverboi-client-bucket",
    });

    const deployment = new BucketDeployment(this, "Bucket-Deployment", {
      sources: [Source.asset("lib/stacks/resources/onboardingDeployment")],
      destinationBucket: this.resourcesBucket,
    });

    this.serverList = new Table(this, "Server-Table", {
      partitionKey: { name: "ServerID", type: AttributeType.STRING },
      tableName: "ServerBoi-Server-List",
    });

    this.linodeTable = new Table(this, "Linode-User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "Linode-User-List",
    });

    this.awsTable = new Table(this, "AWS-User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "AWS-User-List",
    });

    this.userList = new Table(this, "User-Table", {
      partitionKey: { name: "UserID", type: AttributeType.STRING },
      tableName: "ServerBoi-User-List",
    });
  }
}
