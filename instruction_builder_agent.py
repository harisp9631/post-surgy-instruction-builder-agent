"""Core instruction builder agent for generating and adjusting post-surgery instructions."""

from pydantic import BaseModel, Field

from strands import Agent

from prompts_instructions import INSTRUCTION_GENERATION_PROMPT, INSTRUCTION_ADJUSTMENT_PROMPT


class InstructionResponse(BaseModel):
    """Structured output schema for instruction builder responses."""

    instructions: str = Field(
        description="The generated or adjusted post-surgery instruction content for the patient."
    )
    reasoning: str = Field(
        description="Brief explanation of how context or feedback was used to produce the instructions."
    )


def create_instruction_agent(system_prompt: str):
    """
    Create and configure the instruction agent with structured output.

    Args:
        system_prompt: Either INSTRUCTION_GENERATION_PROMPT or INSTRUCTION_ADJUSTMENT_PROMPT.

    Returns:
        Agent: Configured Strands agent for instruction generation or adjustment.
    """
    agent = Agent(
        system_prompt=system_prompt,
        callback_handler=None,
        structured_output_model=InstructionResponse,
    )
    return agent


def build_instruction_input(context: dict) -> str:
    """
    Format context into a prompt for instruction generation.

    Args:
        context: Dict with procedure_id, procedure_type, procedure_status, perform_at,
                 days_post_op, patient_id, patient_name, doctor_name, procedure_history.

    Returns:
        str: Formatted prompt for the agent.
    """
    parts = []
    if context.get("procedure_type"):
        parts.append(f"PROCEDURE TYPE: {context['procedure_type']}")
    if context.get("procedure_status"):
        parts.append(f"PROCEDURE STATUS: {context['procedure_status']}")
    if context.get("perform_at"):
        parts.append(f"PERFORMED AT: {context['perform_at']}")
    if context.get("days_post_op") is not None:
        parts.append(f"DAYS POST-OP: {context['days_post_op']}")
    if context.get("patient_name"):
        parts.append(f"PATIENT: {context['patient_name']}")
    if context.get("doctor_name"):
        parts.append(f"DOCTOR: {context['doctor_name']}")
    if context.get("procedure_history"):
        history = context["procedure_history"]
        if isinstance(history, list):
            lines = [
                f"  - {h.get('type', h.get('procedure_type', '?'))} (id={h.get('id', '?')}, {h.get('perform_at', '')})"
                for h in history
            ]
            parts.append("PROCEDURE HISTORY (this patient):\n" + "\n".join(lines))
        else:
            parts.append(f"PROCEDURE HISTORY: {history}")
    return "\n\n".join(parts) if parts else "No additional context provided."


def build_adjustment_input(message: str, current_instructions: str, context: dict) -> str:
    """
    Format adjustment request into a prompt.

    Args:
        message: Doctor/nurse feedback.
        current_instructions: Existing instruction text.
        context: Same context dict as generation.

    Returns:
        str: Formatted prompt for the agent.
    """
    parts = [
        "FEEDBACK FROM DOCTOR/NURSE:",
        message,
        "",
        "CURRENT INSTRUCTIONS:",
        current_instructions or "(none)",
    ]
    ctx_str = build_instruction_input(context)
    if ctx_str:
        parts.extend(["", "CONTEXT:", ctx_str])
    return "\n".join(parts)


def process_instruction_generation(context: dict) -> dict:
    """
    Generate initial post-surgery instructions from context.

    Args:
        context: Procedure/patient context from Rails.

    Returns:
        dict: {"instructions": str, "reasoning": str}
    """
    agent = create_instruction_agent(INSTRUCTION_GENERATION_PROMPT)
    agent_input = build_instruction_input(context or {})
    result = agent(agent_input)
    structured = result.structured_output
    return {
        "instructions": structured.instructions,
        "reasoning": structured.reasoning,
    }


def process_instruction_adjustment(message: str, current_instructions: str, context: dict) -> dict:
    """
    Adjust existing instructions based on doctor/nurse feedback.

    Args:
        message: Feedback text.
        current_instructions: Current instruction text.
        context: Procedure/patient context.

    Returns:
        dict: {"instructions": str, "reasoning": str}
    """
    agent = create_instruction_agent(INSTRUCTION_ADJUSTMENT_PROMPT)
    agent_input = build_adjustment_input(
        message=message,
        current_instructions=current_instructions or "",
        context=context or {},
    )
    result = agent(agent_input)
    structured = result.structured_output
    return {
        "instructions": structured.instructions,
        "reasoning": structured.reasoning,
    }
