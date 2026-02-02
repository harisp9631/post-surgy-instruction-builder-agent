"""Instruction builder agent for AWS Bedrock AgentCore deployment."""

import logging

from bedrock_agentcore.runtime import BedrockAgentCoreApp

from instruction_builder_agent import process_instruction_generation, process_instruction_adjustment

logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload):
    """
    AgentCore entrypoint for the instruction builder agent.

    Expected payload structure:

    instruction_generation:
    {
        "type": "instruction_generation",
        "context": {
            "procedure_id": 1,
            "procedure_type": "knee replacement",
            "procedure_status": "completed",
            "perform_at": "2026-01-20T10:00:00Z",
            "days_post_op": 6,
            "patient_id": 1,
            "patient_name": "Jane Doe",
            "doctor_name": "Dr. Smith",
            "procedure_history": [...]
        }
    }

    instruction_adjustment:
    {
        "type": "instruction_adjustment",
        "message": "Add a note about avoiding stairs for 2 weeks",
        "current_instructions": "...",
        "context": { ... }
    }

    Returns:
        dict: {"instructions": str, "reasoning": str}
    """
    try:
        payload_type = payload.get("type")
        context = payload.get("context") or {}

        if payload_type == "instruction_generation":
            logging.info("Processing instruction_generation")
            return process_instruction_generation(context)
        if payload_type == "instruction_adjustment":
            message = payload.get("message")
            current_instructions = payload.get("current_instructions", "")
            if message is None:
                return {
                    "error": "Missing required field: message",
                    "instructions": current_instructions,
                    "reasoning": "",
                }
            logging.info("Processing instruction_adjustment")
            return process_instruction_adjustment(
                message=message,
                current_instructions=current_instructions,
                context=context,
            )

        return {
            "error": f"Unknown or missing type: {payload_type}. Use 'instruction_generation' or 'instruction_adjustment'.",
            "instructions": "",
            "reasoning": "",
        }
    except Exception as e:
        logging.error(f"Error processing instruction builder payload: {e}", exc_info=True)
        return {
            "error": str(e),
            "instructions": "",
            "reasoning": "",
        }


if __name__ == "__main__":
    app.run()
