import { Construct, Duration } from "monocdk"
import {
    Function,
    Runtime,
    Tracing,
    Code,
    ILayerVersion
} from "monocdk/aws-lambda";
import { Role, ServicePrincipal } from "monocdk/aws-iam";

export interface PythonLambdaProps {
    name: string
    codePath: string
    handler: string
    memorySize?: number
    timeout?: Duration
    environment?: { [key: string]: string}
    layers?: ILayerVersion[]
}

export class PythonLambda extends Construct {
  public readonly lambda: Function
  constructor(scope: Construct, id: string, props: PythonLambdaProps) {
    super(scope, id);
    
    this.lambda = new Function(this, `${props.name}-Python-Function`, {
        runtime: Runtime.PYTHON_3_8,
        handler: props.handler,
        code: Code.fromAsset(props.codePath),
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