import { Stack, Construct, RemovalPolicy, Duration } from "monocdk";
import { Table, AttributeType, BillingMode } from "monocdk/aws-dynamodb";
import { Bucket } from "monocdk/aws-s3";
import { BucketDeployment, Source } from "monocdk/aws-s3-deployment";
import { Secret } from "monocdk/aws-secretsmanager";

export class ServerlessBoiResourcesStack extends Stack {
  //Creates all resources referenced across stacks
  readonly resourcesBucket: Bucket;
  readonly clientBucket: Bucket;
  readonly tokenBucket: Bucket;
  readonly webhookList: Table;
  readonly serverList: Table;
  readonly ownerList: Table;
  readonly channelTable: Table;
  readonly discordToken: string;
  readonly provisionConfigBucket: Bucket;
  readonly dockerComposeBucket: Bucket;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    const discordToken = Secret.fromSecretCompleteArn(
      this,
      " ServerBoi-Discord-Token",
      "arn:aws:secretsmanager:us-west-2:518723822228:secret:ServerBoi-Discord-Token-RBBLnM"
    );
    this.discordToken = discordToken.secretValue.toString()

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

    this.provisionConfigBucket = new Bucket(this, "Config-Bucket", {
      bucketName: "serverboi-configuration-bucket",
      removalPolicy: RemovalPolicy.DESTROY,
    })

    this.dockerComposeBucket = new Bucket(this, "Compose-Template-Bucket", {
      bucketName: "serverboi-docker-compose-bucket",
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

    this.channelTable = new Table(this, "Channel-Table", {
      partitionKey: { name: "GuildID", type: AttributeType.STRING },
      tableName: "ServerBoi-Channel-Table",
      removalPolicy: RemovalPolicy.DESTROY,
      billingMode: BillingMode.PAY_PER_REQUEST
  });

    this.webhookList = new Table(this, "Webhook-Table", {
      partitionKey: { name: "GuildID", type: AttributeType.STRING },
      tableName: "ServerBoi-Webhook-List",
      removalPolicy: RemovalPolicy.DESTROY,
      billingMode: BillingMode.PAY_PER_REQUEST
    });

    this.serverList = new Table(this, "Server-Table", {
      partitionKey: { name: "ServerID", type: AttributeType.STRING },
      tableName: "ServerBoi-Server-List",
      removalPolicy: RemovalPolicy.DESTROY,
      billingMode: BillingMode.PAY_PER_REQUEST
    });

    this.ownerList = new Table(this, "Owner-Table", {
      partitionKey: { name: "OwnerID", type: AttributeType.STRING },
      tableName: "ServerBoi-Owner-List",
      removalPolicy: RemovalPolicy.DESTROY,
      billingMode: BillingMode.PAY_PER_REQUEST
    })
  }
}
