import { Stack, StackProps, Construct, Duration } from "monocdk";
import { Table, AttributeType, Attribute } from "monocdk/aws-dynamodb";
import { Bucket } from "monocdk/aws-s3";
import { BucketDeployment, Source } from "monocdk/aws-s3-deployment";
import { OnboardingConstruct } from "./OnboardCfnDeployment";
import { SynthUtils } from "@monocdk-experiment/assert";

export class ServerlessBoiResourcesStack extends Stack {
  //Creates all resources referenced across stacks
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const resourcesBucket = new Bucket(this, "Resources-Bucket", {
      bucketName: "serverboi-resources-bucket",
    });

    const deployment = new BucketDeployment(this, "Bucket-Deployment", {
      sources: [Source.asset("lib/stacks/resources/onboardingDeployment")],
      destinationBucket: resourcesBucket,
    });

    const serverList = new Table(this, "Server-List", {
      partitionKey: { name: "server_id", type: AttributeType.NUMBER },
      tableName: "ServerlessBoi-Server-List",
    });

    serverList.addGlobalSecondaryIndex({
      indexName: "Game",
      partitionKey: { name: "game", type: AttributeType.STRING },
    });
  }
}
