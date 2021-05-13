import { Construct, Duration } from "monocdk"
import { Bucket } from "monocdk/aws-s3";
import { Queue } from "monocdk/aws-sqs" 
import { PythonLambda } from "./PythonLambdaConstruct"
import { SqsEventSource } from "monocdk/lib/aws-lambda-event-sources";
import { PolicyStatement } from "monocdk/aws-iam";


export class WaitForBootstrap extends Construct {
  public readonly tokenQueue: Queue
  public readonly tokenBucket: Bucket

  constructor(scope: Construct, id: string) {
    super(scope, id);

    this.tokenQueue = new Queue(this, "Wait-For-Bootstrap", {
      queueName: "Wait-For-Bootstrap-Tokens"
    })

    this.tokenBucket = new Bucket(this, "Token-Bucket", {
      bucketName: "serverboi-provision-token-bucket",
      publicReadAccess: true,
      lifecycleRules: [{
        expiration: Duration.days(1)
      }]
    })

    const getTokenName = "Get-Token";
    const getToken = new PythonLambda(this, getTokenName, {
      name: getTokenName,
      codePath: "lambdas/handlers/get_token",
      handler: "get_token.main.lambda_handler",
      environment:{
          TOKEN_QUEUE: this.tokenQueue.queueName,
          TOKEN_BUCKET: this.tokenBucket.bucketName
      },
    })

    getToken.lambda.addEventSource(new SqsEventSource(this.tokenQueue))
    getToken.lambda.addToRolePolicy(
      new PolicyStatement({
        resources: ["*"],
        actions: [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "s3:PutObject",
        ],
      })
    )
  }
}