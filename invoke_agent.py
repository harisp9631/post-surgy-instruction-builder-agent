"""Script to invoke the deployed instruction builder agent."""

import argparse
import json
import sys
import uuid

import boto3


def invoke_agent(
    agent_runtime_arn: str,
    payload: dict,
    session_id: str = None,
    region: str = "us-east-1",
):
    """Invoke the instruction builder agent with the given payload."""
    if session_id is None:
        session_id = f"inst-{uuid.uuid4().hex}"
    try:
        client = boto3.client("bedrock-agentcore", region_name=region)
        payload_str = json.dumps(payload)
        print("=" * 70)
        print("Invoking Instruction Builder Agent")
        print("=" * 70)
        print(f"\nPayload type: {payload.get('type', '?')}")
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
        print("=" * 70)
        if "instructions" in response_data:
            print("Instructions:")
            print(response_data["instructions"])
            if response_data.get("reasoning"):
                print("\nReasoning:", response_data["reasoning"])
        else:
            print(json.dumps(response_data, indent=2))
        print("=" * 70)
        return response_data
    except Exception as e:
        print(f"\n❌ Error invoking agent: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Invoke the Post-Surgery Instruction Builder Agent on AWS Bedrock AgentCore"
    )
    parser.add_argument("--arn", required=True, help="Agent Runtime ARN (from deployment)")
    parser.add_argument("--type", choices=["instruction_generation", "instruction_adjustment"], help="Payload type")
    parser.add_argument("--payload", help="JSON payload file path (or inline JSON string)")
    parser.add_argument("--region", default="us-east-1", help="AWS region")
    parser.add_argument("--session-id", help="Session ID (auto-generated if not provided)")
    args = parser.parse_args()

    if args.payload:
        try:
            with open(args.payload) as f:
                data = json.load(f)
            # Support test_payloads.json format: list of {description, payload}
            if isinstance(data, list) and len(data) > 0:
                payload = data[0].get("payload", data[0])
            else:
                payload = data
        except FileNotFoundError:
            try:
                payload = json.loads(args.payload)
            except json.JSONDecodeError:
                print("Error: --payload must be a file path or valid JSON string")
                sys.exit(1)
    elif args.type == "instruction_generation":
        payload = {
            "type": "instruction_generation",
            "context": {
                "procedure_type": "knee replacement",
                "days_post_op": 6,
                "patient_name": "Jane Doe",
                "doctor_name": "Dr. Smith",
            },
        }
    elif args.type == "instruction_adjustment":
        payload = {
            "type": "instruction_adjustment",
            "message": "Add a note about avoiding stairs for 2 weeks",
            "current_instructions": "Rest as needed. Keep the wound clean. Take pain medication as prescribed.",
            "context": {"procedure_type": "knee replacement", "days_post_op": 6},
        }
    else:
        print("Error: Provide --payload <file|json> or --type instruction_generation|instruction_adjustment")
        sys.exit(1)

    invoke_agent(
        agent_runtime_arn=args.arn,
        payload=payload,
        session_id=args.session_id,
        region=args.region,
    )


if __name__ == "__main__":
    main()
