import main
context = ''
event = {
   "resource":"/discord",
   "path":"/discord",
   "httpMethod":"POST",
   "headers":{
      "Accept":"*/*",
      "CloudFront-Forwarded-Proto":"https",
      "CloudFront-Is-Desktop-Viewer":"true",
      "CloudFront-Is-Mobile-Viewer":"false",
      "CloudFront-Is-SmartTV-Viewer":"false",
      "CloudFront-Is-Tablet-Viewer":"false",
      "CloudFront-Viewer-Country":"US",
      "content-type":"application/json",
      "Host":"2v6dqgxqlb.execute-api.us-west-2.amazonaws.com",
      "User-Agent":"Discord-Interactions/1.0 (+https://discord.com)",
      "Via":"1.1 c8c63d354ed6e5aa834ef3f7e476e87c.cloudfront.net (CloudFront)",
      "X-Amz-Cf-Id":"6G8NAHuXYKRHO7P5lg3xAomsaKesdYk82sFQy4mlor8E32cS4j55_g==",
      "X-Amzn-Trace-Id":"Root=1-6090dd59-723119ce5fa298cb5286d158",
      "X-Forwarded-For":"35.227.62.178, 52.46.25.140",
      "X-Forwarded-Port":"443",
      "X-Forwarded-Proto":"https",
      "x-signature-ed25519":"29eb6b5b32e6d4daf629afe9dc96d23d75f456907d4465f84f936fc4fab7ef3b72346fe6c9c8b54e00ffc7453fea617695a32719bee741ff8ad50a768c61ac05",
      "x-signature-timestamp":"1620106585"
   },
   "multiValueHeaders":{
      "Accept":[
         "*/*"
      ],
      "CloudFront-Forwarded-Proto":[
         "https"
      ],
      "CloudFront-Is-Desktop-Viewer":[
         "true"
      ],
      "CloudFront-Is-Mobile-Viewer":[
         "false"
      ],
      "CloudFront-Is-SmartTV-Viewer":[
         "false"
      ],
      "CloudFront-Is-Tablet-Viewer":[
         "false"
      ],
      "CloudFront-Viewer-Country":[
         "US"
      ],
      "content-type":[
         "application/json"
      ],
      "Host":[
         "2v6dqgxqlb.execute-api.us-west-2.amazonaws.com"
      ],
      "User-Agent":[
         "Discord-Interactions/1.0 (+https://discord.com)"
      ],
      "Via":[
         "1.1 c8c63d354ed6e5aa834ef3f7e476e87c.cloudfront.net (CloudFront)"
      ],
      "X-Amz-Cf-Id":[
         "6G8NAHuXYKRHO7P5lg3xAomsaKesdYk82sFQy4mlor8E32cS4j55_g=="
      ],
      "X-Amzn-Trace-Id":[
         "Root=1-6090dd59-723119ce5fa298cb5286d158"
      ],
      "X-Forwarded-For":[
         "35.227.62.178, 52.46.25.140"
      ],
      "X-Forwarded-Port":[
         "443"
      ],
      "X-Forwarded-Proto":[
         "https"
      ],
      "x-signature-ed25519":[
         "29eb6b5b32e6d4daf629afe9dc96d23d75f456907d4465f84f936fc4fab7ef3b72346fe6c9c8b54e00ffc7453fea617695a32719bee741ff8ad50a768c61ac05"
      ],
      "x-signature-timestamp":[
         "1620106585"
      ]
   },
   "queryStringParameters":"None",
   "multiValueQueryStringParameters":"None",
   "pathParameters":"None",
   "stageVariables":"None",
   "requestContext":{
      "resourceId":"dsn728",
      "resourcePath":"/discord",
      "httpMethod":"POST",
      "extendedRequestId":"eyeGDEilPHcFucg=",
      "requestTime":"04/May/2021:05:36:25 +0000",
      "path":"/prod/discord",
      "accountId":"742762521158",
      "protocol":"HTTP/1.1",
      "stage":"prod",
      "domainPrefix":"2v6dqgxqlb",
      "requestTimeEpoch":1620106585893,
      "requestId":"1fb3ab5c-3271-4559-8219-ddf07a83952e",
      "identity":{
         "cognitoIdentityPoolId":"None",
         "accountId":"None",
         "cognitoIdentityId":"None",
         "caller":"None",
         "sourceIp":"35.227.62.178",
         "principalOrgId":"None",
         "accessKey":"None",
         "cognitoAuthenticationType":"None",
         "cognitoAuthenticationProvider":"None",
         "userArn":"None",
         "userAgent":"Discord-Interactions/1.0 (+https://discord.com)",
         "user":"None"
      },
      "domainName":"2v6dqgxqlb.execute-api.us-west-2.amazonaws.com",
      "apiId":"2v6dqgxqlb"
   },
   "body":"{\"application_id\":\"713857439220367432\",\"channel_id\":\"242453642362355712\",\"data\":{\"id\":\"824124806798114867\",\"name\":\"serverboi\",\"options\":[{\"name\":\"onboard\",\"options\":[{\"name\":\"aws\",\"type\":1}],\"type\":2}]},\"guild_id\":\"170364850256609280\",\"id\":\"839012573075996743\",\"member\":{\"deaf\":false,\"is_pending\":false,\"joined_at\":\"2019-07-21T06:03:24.405000+00:00\",\"mute\":false,\"nick\":null,\"pending\":false,\"permissions\":\"17179869183\",\"premium_since\":\"2020-09-24T21:06:09.945000+00:00\",\"roles\":[\"174372617623568384\",\"256562231221813249\",\"286278364959080448\",\"396598266004897795\",\"398300800461570052\",\"585650602504093716\",\"599778569937485824\",\"637013068710412289\",\"637651699133317125\",\"691350575219998720\",\"825130289893212201\"],\"user\":{\"avatar\":\"f94fefe611b5269790819e019aa8f849\",\"discriminator\":\"6969\",\"id\":\"155875705417236480\",\"public_flags\":0,\"username\":\"Awlsring\"}},\"token\":\"aW50ZXJhY3Rpb246ODM5MDEyNTczMDc1OTk2NzQzOkRNdXZIaW9NZHhFN0d3NGVTVG9XNDcyZmJGcFl4U085TWNlcVRacjRBaEF0U0llQllCdzhPQnl0R3IzR3lkTmlvYTlWQXp4cndRd0tPSW42MDNyRjFOY3dNNzFISktyOEQwWjZyakl3M0NCRTNpVW1qcEFuWXNNWjdOQ0pNWU92\",\"type\":2,\"version\":1}",
   "isBase64Encoded":False
}

def test_import():
    import os
    assert True

def test_lambda():
    main.lambda_handler(event, context)
    assert True