import { Stack, StackProps, Construct } from "monocdk";
import { CdkPipeline, SimpleSynthAction } from "monocdk/pipelines";
import { Artifact } from "monocdk/aws-codepipeline";
import { CodeStarConnectionsSourceAction } from "monocdk/aws-codepipeline-actions";

export class PipelineStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const sourceArtifact = new Artifact();
    const cloudAssemblyArtifact = new Artifact();

    const pipeline = new CdkPipeline(this, "ServerlessBoi-Pipeline", {
      pipelineName: "ServerlessBoi-Pipeline",
      selfMutating: true,
      cloudAssemblyArtifact: cloudAssemblyArtifact,

      sourceAction: new CodeStarConnectionsSourceAction({
        actionName: "Codestar",
        connectionArn:
          "arn:aws:codestar-connections:us-west-2:742762521158:connection/a6558ce6-91cc-430f-a5e8-0a9507d9753a",
        output: sourceArtifact,
        owner: "Awlsring",
        repo: "ServerlessBoi",
        branch: "main",
      }),

      synthAction: SimpleSynthAction.standardNpmSynth({
        sourceArtifact,
        cloudAssemblyArtifact,
        installCommand: "npm ci",
        buildCommand: "npm run build",
      }),
    });
  }
}
