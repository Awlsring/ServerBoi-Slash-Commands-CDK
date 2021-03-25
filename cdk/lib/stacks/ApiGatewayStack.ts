import {Stack, StackProps, Construct, Duration} from 'monocdk';
import {RestApi, LambdaIntegration, PassthroughBehavior} from 'monocdk/aws-apigateway'
import {Function, Runtime, Tracing, Code, LayerVersion} from 'monocdk/aws-lambda'
import {Role, ServicePrincipal, PolicyStatement} from 'monocdk/aws-iam'

export class ApiGatewayStack extends Stack {
  //Creates all resources needed for the API Gateway
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lambda = new Function(this, 'TestLambda', {
      runtime: Runtime.PYTHON_3_8,
      handler: 'test.lambda_handler',
      code: Code.fromAsset('../lambda/handlers'),
      memorySize: 128,
      tracing: Tracing.ACTIVE,
      timeout: Duration.seconds(5),
      functionName: 'test-function',
      role: new Role(this, 'test-role', {
        assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
        roleName: 'Test-Function'
      })
    })

    const api = new RestApi(this, "Discord-Endpoint")

    const discord = api.root.addResource('discord')

    discord.addMethod('Post', new LambdaIntegration(lambda, {
        proxy: false,
        passthroughBehavior: PassthroughBehavior.NEVER,
        requestTemplates: {
          'application/json': `{ 
            "username": "$input.params('username')",
            "region": "$input.params('region')"
        }`,
        },
        integrationResponses: [{
            statusCode: '200',
            responseParameters: {
                "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'OPTIONS,GET'",
                "method.response.header.Access-Control-Allow-Origin": "'*'"
              },
        }]}), {
        methodResponses: [{ 
            statusCode: '200',
            responseParameters: {
                'method.response.header.Access-Control-Allow-Headers': true,
                'method.response.header.Access-Control-Allow-Methods': true,
                'method.response.header.Access-Control-Allow-Credentials': true,
                'method.response.header.Access-Control-Allow-Origin': true,
            },
        }]
    })
  }
}
