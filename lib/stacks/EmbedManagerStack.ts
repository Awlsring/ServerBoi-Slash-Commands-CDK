import { Construct, RemovalPolicy, Stack, StackProps } from "monocdk";
import { AttributeType, BillingMode, Table } from "monocdk/aws-dynamodb";
import { GoLambda } from "../constructs/GoLambdaConstruct";
import { EmbedManager } from "../../function_uri_list.json"

export interface EmbedManagerStackProps extends StackProps {
    readonly serverList: Table;
    readonly discordToken: string;
  }
  
  export class EmbedManagerStack extends Stack {
    public readonly channelList: Table

    constructor(scope: Construct, id: string, props: EmbedManagerStackProps) {
        super(scope, id, props);

        this.channelList = new Table(this, "Channel-List", {
            partitionKey: { name: "GuildID", type: AttributeType.STRING },
            tableName: "ServerBoi-Channel-List",
            removalPolicy: RemovalPolicy.DESTROY,
            billingMode: BillingMode.PAY_PER_REQUEST
        });
    
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
        
    }
}