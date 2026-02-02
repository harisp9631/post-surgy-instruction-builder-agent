"""Deployment script for deploying the instruction builder agent to AWS Bedrock AgentCore."""

import json
import os
import sys

import boto3
from botocore.exceptions import ClientError


def create_agent_runtime(
    agent_name: str,
    container_uri: str,
    role_arn: str,
    region: str = "us-east-1",
):
    """Create an AgentCore runtime deployment."""
    try:
        client = boto3.client("bedrock-agentcore-control", region_name=region)
        print(f"Creating AgentCore runtime: {agent_name}")
        print(f"Container URI: {container_uri}")
        print(f"Role ARN: {role_arn}")
        print(f"Region: {region}")
        print("-" * 70)
        response = client.create_agent_runtime(
            agentRuntimeName=agent_name,
            agentRuntimeArtifact={
                "containerConfiguration": {"containerUri": container_uri}
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=role_arn,
        )
        print("\n✓ Agent Runtime created successfully!")
        print(f"Agent Runtime ARN: {response['agentRuntimeArn']}")
        print(f"Status: {response['status']}")
        return response
    except ClientError as e:
        print(f"\n❌ Error creating agent runtime: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


def invoke_agent(
    agent_runtime_arn: str,
    payload: dict,
    session_id: str,
    region: str = "us-east-1",
):
    """Invoke the deployed instruction builder agent."""
    try:
        client = boto3.client("bedrock-agentcore", region_name=region)
        payload_str = json.dumps(payload)
        print(f"\nInvoking agent with type: {payload.get('type', '?')}")
        print(f"Session ID: {session_id}")
        print("-" * 70)
        response = client.invoke_agent_runtime(
            agentRuntimeArn=agent_runtime_arn,
            runtimeSessionId=session_id,
            payload=payload_str,
            qualifier="DEFAULT",
        )
        response_body = response["response"].read()
        response_data = json.loads(response_body)
        print("\n✓ Agent Response:")
        print(json.dumps(response_data, indent=2))
        return response_data
    except ClientError as e:
        print(f"\n❌ Error invoking agent: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


def verify_aws_account(expected_account_id: str = None):
    """Verify we're deploying to the correct AWS account."""
    try:
        client = boto3.client("sts")
        identity = client.get_caller_identity()
        current_account = identity["Account"]
        current_user = identity.get("Arn", "Unknown")
        print(f"Current AWS Account: {current_account}")
        print(f"Current User/Role: {current_user}")
        if expected_account_id and current_account != expected_account_id:
            print(f"\n❌ ERROR: Account mismatch!")
            print(f"   Expected: {expected_account_id}")
            print(f"   Current:  {current_account}")
            sys.exit(1)
        print("✓ Account verified")
        return current_account
    except Exception as e:
        print(f"❌ Error verifying AWS account: {e}")
        sys.exit(1)


def main():
    print("=" * 70)
    print("Post-Surgery Instruction Builder Agent - AgentCore Deployment")
    print("=" * 70)
    print()
    config = {
        "agent_name": "post-surgy-instruction-builder-agent",
        "container_uri": "<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/post-surgy-instruction-builder-agent:latest",
        "role_arn": "arn:aws:iam::<ACCOUNT_ID>:role/AgentRuntimeRole",
        "region": "us-east-1",
        "expected_account_id": None,
    }
    config["container_uri"] = os.getenv("AGENTCORE_CONTAINER_URI", config["container_uri"])
    config["role_arn"] = os.getenv("AGENTCORE_ROLE_ARN", config["role_arn"])
    config["region"] = os.getenv("AGENTCORE_REGION", config["region"])
    config["expected_account_id"] = os.getenv("AGENTCORE_EXPECTED_ACCOUNT", config["expected_account_id"])

    print("Verifying AWS account...")
    print("-" * 70)
    current_account = verify_aws_account(config["expected_account_id"])
    print("-" * 70)
    print()

    if "<ACCOUNT_ID>" in config["container_uri"]:
        print("⚠️  Configuration Required!")
        print("\nUpdate config in this script or use environment variables:")
        print(f"  export AGENTCORE_CONTAINER_URI='{current_account}.dkr.ecr.{config['region']}.amazonaws.com/post-surgy-instruction-builder-agent:latest'")
        print(f"  export AGENTCORE_ROLE_ARN='arn:aws:iam::{current_account}:role/AgentRuntimeRole'")
        print(f"  export AGENTCORE_REGION='{config['region']}'")
        sys.exit(1)

    response = create_agent_runtime(
        agent_name=config["agent_name"],
        container_uri=config["container_uri"],
        role_arn=config["role_arn"],
        region=config["region"],
    )
    agent_runtime_arn = response["agentRuntimeArn"]

    print("\n" + "=" * 70)
    print("Testing Agent Invocation (instruction_generation)")
    print("=" * 70)
    test_payload = {
        "type": "instruction_generation",
        "context": {
            "procedure_type": "knee replacement",
            "days_post_op": 6,
            "patient_name": "Test Patient",
            "doctor_name": "Dr. Smith",
        },
    }
    session_id = "test-session-instruction-builder-12345678901234567890"
    invoke_agent(
        agent_runtime_arn=agent_runtime_arn,
        payload=test_payload,
        session_id=session_id,
        region=config["region"],
    )

    print("\n" + "=" * 70)
    print("Deployment Complete!")
    print("=" * 70)
    print(f"\nAgent ARN: {agent_runtime_arn}")
    print("\nSet in Rails .env:")
    print(f"  BEDROCK_INSTRUCTION_BUILDER_AGENT_RUNTIME_ARN={agent_runtime_arn}")


if __name__ == "__main__":
    main()
