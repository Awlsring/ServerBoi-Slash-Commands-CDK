import { Construct, Stack, StackProps } from "monocdk";
import { Table } from "monocdk/aws-dynamodb";
import { GoLambda } from "../constructs/GoLambdaConstruct";
import { EmbedManager } from "../../function_uri_list.json"
import { PolicyStatement } from "monocdk/aws-iam";

export interface EmbedManagerStackProps extends StackProps {
    readonly serverList: Table;
    readonly discordToken: string;
  }
  
  export class EmbedManagerStack extends Stack {
    constructor(scope: Construct, id: string, props: EmbedManagerStackProps) {
        super(scope, id, props);
    
        const embedManagerName = "Embed-Manager-Lambda-Go";
        const embedManager = new GoLambda(this, embedManagerName, {
          name: embedManagerName,
          bucket: EmbedManager.bucket,
          object: EmbedManager.key,
          environment: {
            SERVER_TABLE: props.serverList.tableName,
            DISCORD_TOKEN: props.discordToken,
            STAGE: "Prod"
          },
        });
        embedManager.lambda.addToRolePolicy(
            new PolicyStatement({
              resources: ["*"],
              actions: [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "dynamodb:GetItem",
                "sts:AssumeRole",
              ],
            })
          );
        
    }
}