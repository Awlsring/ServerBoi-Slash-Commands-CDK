import { Stack, StackProps, Construct, Duration } from 'monocdk';
import { Table, AttributeType, Attribute } from 'monocdk/aws-dynamodb'

export class ResourcesStack extends Stack {
  //Creates all resources referenced across stacks
  constructor(scope: Construct, id: string) {
    super(scope, id)

    const serverList = new Table(this, "Server-List", {
        partitionKey: { name: 'server_id', type: AttributeType.NUMBER },
        tableName: "ServerlessBoi-Server-List",
    })

    serverList.addGlobalSecondaryIndex({
        indexName: "Game",
        partitionKey: { name: 'game', type: AttributeType.STRING }
    })
  }
}