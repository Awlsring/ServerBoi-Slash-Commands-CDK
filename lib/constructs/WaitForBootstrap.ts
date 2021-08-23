import { Construct, Duration, RemovalPolicy } from "monocdk"
import { Bucket } from "monocdk/aws-s3";
import { Queue } from "monocdk/aws-sqs" 


export class WaitForBootstrap extends Construct {
  public readonly tokenQueue: Queue
  public readonly tokenBucket: Bucket

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.tokenQueue = new Queue(this, "Wait-For-Bootstrap", {
      queueName: "Wait-For-Bootstrap-Tokens",
      visibilityTimeout: Duration.seconds(30)
    })

    this.tokenBucket = new Bucket(this, "Token-Bucket", {
      bucketName: "serverboi-provision-token-bucket",
      publicReadAccess: true,
      autoDeleteObjects: true,
      removalPolicy: RemovalPolicy.DESTROY,
      lifecycleRules: [{
        expiration: Duration.days(1)
      }],
    })
  }
}