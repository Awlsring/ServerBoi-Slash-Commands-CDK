import { Stack, StackProps, Construct, Duration } from "monocdk";
import {
  Role,
  AccountPrincipal,
  Effect,
  PolicyDocument,
  PolicyStatement,
  ManagedPolicy,
  Policy,
} from "monocdk/aws-iam";

export class OnboardingConstruct extends Stack {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const assumedRolePolicyDocument = new PolicyDocument({
      statements: [
        new PolicyStatement({
          resources: ["*"],
          effect: Effect.ALLOW,
          actions: ["*"],
          conditions: {
            StringEquals: {
              "ec2:ResourceTag/Owner": "${aws:username}",
            },
          },
        }),
      ],
    });

    const assumedRolePolicy = new ManagedPolicy(this, "managed-policy", {
      document: assumedRolePolicyDocument,
      description: "",
      managedPolicyName: "ServerBoi-Resource.Assumed-Role-Policy",
    });

    const role = new Role(this, "Role", {
      assumedBy: new AccountPrincipal("account_id"),
      description:
        "Allows ServerBoi to perform actions on resources in account.",
      roleName: "ServerBoi-Resource.Assumed-Role",
      managedPolicies: [assumedRolePolicy],
    });
  }
}
