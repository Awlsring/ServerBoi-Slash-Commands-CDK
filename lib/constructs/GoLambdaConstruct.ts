import { Construct, Duration } from "monocdk"
import {
    Function,
    Runtime,
    Tracing,
    Code,
    ILayerVersion
} from "monocdk/aws-lambda";
import { Bucket } from "monocdk/aws-s3";
import { Role, ServicePrincipal } from "monocdk/aws-iam";

export interface GoLambdaProps {
    name: string
    bucket: string
    object: string
    handler?: string
    memorySize?: number
    timeout?: Duration
    environment?: { [key: string]: string}
    layers?: ILayerVersion[]
}

export class GoLambda extends Construct {
  public readonly lambda: Function
  constructor(scope: Construct, id: string, props: GoLambdaProps) {
    super(scope, id);

    const packageBucket = Bucket.fromBucketName(this, "Package-Bucket", props.bucket)
    
    this.lambda = new Function(this, `${props.name}-Go-Function`, {
        runtime: Runtime.GO_1_X,
        handler: props.handler ?? "main",
        code: Code.fromBucket(packageBucket, props.object),
        memorySize: props.memorySize ?? 128,
        tracing: Tracing.ACTIVE,
        timeout: props.timeout ?? Duration.seconds(60),
        layers: props.layers ?? [],
        functionName: props.name,
        environment: props.environment,
        role: new Role(this, `${props.name}-Role`, {
          assumedBy: new ServicePrincipal("lambda.amazonaws.com"),
          roleName: `${props.name}-Role`,
        }),
      })

  }
}