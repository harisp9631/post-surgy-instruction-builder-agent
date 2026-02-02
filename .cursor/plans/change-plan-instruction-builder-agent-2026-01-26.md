---
title: "Change Plan: Instruction Builder Agent for Post-Surgery"
type: "change_plan"
planned_at: "2026-01-26T18:00:00Z"
planned_by: "agent"
scope: "medium"
change_type: "feature"
status: "draft"
tags: ["agent", "bedrock", "agentcore", "strands", "instructions", "python"]
---

# Change Plan: Instruction Builder Agent for Post-Surgery

## Executive Summary

Create a new AWS Bedrock AgentCore agent for generating and adjusting post-surgery patient instructions. This agent will follow the same pattern and approach as the existing post-surgy-patient-agent, using Strands agents with structured output. The agent will handle two operation types: instruction generation (initial creation) and instruction adjustment (modifications based on doctor/nurse feedback).

## Current State

The Rails application (`AgentInstructionBuilderService`) currently invokes a Bedrock agent but the agent implementation doesn't exist yet. The service expects:
- Payload with `type: 'instruction_generation'` or `type: 'instruction_adjustment'`
- Context including procedure details, patient info, doctor name, days post-op, etc.
- Response with `instructions` (or `message`) and `reasoning` (or `reasoning_logic`) fields

The existing `post-surgy-patient-agent` provides a reference implementation using:
- Bedrock AgentCore runtime with Strands agents
- Pydantic models for structured output
- System prompts for agent behavior
- Docker containerization for deployment
- `.bedrock_agentcore.yaml` for configuration

## Desired State

After implementation:
- New `post-surgy-instruction-builder-agent` project following the same structure as `post-surgy-patient-agent`
- Agent handles `instruction_generation` type: generates comprehensive post-surgery instructions based on procedure context
- Agent handles `instruction_adjustment` type: modifies existing instructions based on doctor/nurse feedback
- Structured output with `instructions` and `reasoning` fields
- Deployed to AWS Bedrock AgentCore with separate ARN from patient agent
- Rails service can invoke the agent using the new ARN

## Task Breakdown

### Phase 1: Project Structure and Core Agent

#### Task 1.1: Create Project Directory Structure
- **Type**: create
- **Files**: New directory `post-surgy-instruction-builder-agent/` with initial files
- **Complexity**: low
- **Risk**: low
- **Dependencies**: None
- **Description**: 
  - Create project directory following same structure as `post-surgy-patient-agent`
  - Initialize with `__init__.py`, `.gitignore`, `requirements.txt`
  - Copy structure: `agent_agentcore.py`, `instruction_builder_agent.py`, `prompts_instructions.py`

#### Task 1.2: Create Requirements and Dependencies
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/requirements.txt`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 1.1
- **Description**:
  - Copy requirements from patient agent: `strands-agents>=1.0.0`, `bedrock-agentcore>=0.1.0`, `pydantic>=2.0.0`, `python-dotenv>=1.0.0`, `aws-opentelemetry-distro>=0.10.1`, `boto3>=1.28.0`
  - Ensure Python 3.11+ compatibility

#### Task 1.3: Create Instruction Response Pydantic Model
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/instruction_builder_agent.py`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 1.1
- **Description**:
  - Create `InstructionResponse` Pydantic model with fields:
    - `instructions: str` - The generated/adjusted instruction content
    - `reasoning: str` - The agent's reasoning for the instructions
  - Follow same pattern as `ClarificationResponse` in patient agent

#### Task 1.4: Create System Prompts for Instruction Building
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/prompts_instructions.py`
- **Complexity**: medium
- **Risk**: medium
- **Dependencies**: Task 1.1
- **Description**:
  - Create `INSTRUCTION_GENERATION_PROMPT`: System prompt for generating initial instructions
  - Create `INSTRUCTION_ADJUSTMENT_PROMPT`: System prompt for adjusting existing instructions
  - Include guidelines for:
    - Medical accuracy and safety
    - Procedure-specific considerations
    - Days post-op relevance
    - Clear, patient-friendly language
    - What to include/exclude in instructions

### Phase 2: Agent Implementation

#### Task 2.1: Implement Instruction Builder Agent Core Logic
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/instruction_builder_agent.py`
- **Complexity**: medium
- **Risk**: medium
- **Dependencies**: Task 1.3, Task 1.4
- **Description**:
  - Create `create_instruction_agent()` function that returns Strands Agent with structured output
  - Create `build_instruction_input()` function to format context into agent prompt
  - Create `process_instruction_generation()` function for initial instruction creation
  - Create `process_instruction_adjustment()` function for instruction modifications
  - Follow same pattern as `clarification_agent.py` in patient agent

#### Task 2.2: Implement AgentCore Entrypoint
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/agent_agentcore.py`
- **Complexity**: medium
- **Risk**: medium
- **Dependencies**: Task 2.1
- **Description**:
  - Create `invoke(payload)` entrypoint function decorated with `@app.entrypoint`
  - Handle payload structure:
    - `type: 'instruction_generation'` with `context` field
    - `type: 'instruction_adjustment'` with `message`, `current_instructions`, `context` fields
  - Route to appropriate processing function based on type
  - Return structured response with `instructions` and `reasoning` fields
  - Include error handling and validation
  - Follow same pattern as `agent_agentcore.py` in patient agent

#### Task 2.3: Create Test Payloads
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/test_payloads.json`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 2.2
- **Description**:
  - Create test payloads for instruction_generation with various procedure types
  - Create test payloads for instruction_adjustment with different feedback scenarios
  - Include edge cases: missing context, invalid types, etc.

### Phase 3: Deployment Configuration

#### Task 3.1: Create Dockerfile for AgentCore
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/Dockerfile.agentcore`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 1.2
- **Description**:
  - Copy Dockerfile structure from patient agent
  - Use `python:3.11-slim-bookworm` base image
  - Platform: `linux/arm64`
  - Install dependencies from requirements.txt
  - Copy agent files
  - Expose port 8080
  - Health check endpoint
  - Run with OpenTelemetry instrumentation

#### Task 3.2: Create Bedrock AgentCore Configuration
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/.bedrock_agentcore.yaml`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 2.2
- **Description**:
  - Configure agent with name: `post_surgy_instruction_builder_agent`
  - Set entrypoint to `agent_agentcore.py`
  - Configure runtime: `PYTHON_3_13`
  - Platform: `linux/arm64`
  - Use same AWS account, region, and execution role as patient agent
  - Set network mode: `PUBLIC`
  - Configure observability: enabled

#### Task 3.3: Create Deployment Script
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/deploy_agentcore.py`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 3.1, Task 3.2
- **Description**:
  - Copy deployment script structure from patient agent
  - Update agent name and configuration
  - Include verification and testing steps

#### Task 3.4: Create Invocation Script
- **Type**: create
- **Files**: `post-surgy-instruction-builder-agent/invoke_agent.py`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 2.2
- **Description**:
  - Copy invocation script from patient agent
  - Update for instruction builder payload structure
  - Support both instruction_generation and instruction_adjustment types
  - Include interactive mode for testing

### Phase 4: Integration with Rails

#### Task 4.1: Update Rails Environment Variables
- **Type**: modify
- **Files**: `.env.example` or environment configuration
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 3.2
- **Description**:
  - Add `BEDROCK_INSTRUCTION_BUILDER_AGENT_RUNTIME_ARN` environment variable
  - Document the new ARN for instruction builder agent
  - Keep existing `BEDROCK_AGENT_RUNTIME_ARN` for patient communication agent

#### Task 4.2: Update AgentInstructionBuilderService to Use New ARN
- **Type**: modify
- **Files**: `app/services/agent_instruction_builder_service.rb`
- **Complexity**: low
- **Risk**: low
- **Dependencies**: Task 4.1
- **Description**:
  - Update `@agent_runtime_arn` to use `BEDROCK_INSTRUCTION_BUILDER_AGENT_RUNTIME_ARN` instead of `BEDROCK_AGENT_RUNTIME_ARN`
  - Ensure payload structure matches what agent expects
  - Verify response parsing handles `instructions` and `reasoning` fields correctly

## Impact Analysis

### Files to Create
- `post-surgy-instruction-builder-agent/` - New project directory
- `post-surgy-instruction-builder-agent/__init__.py` - Python package init
- `post-surgy-instruction-builder-agent/.gitignore` - Git ignore rules
- `post-surgy-instruction-builder-agent/requirements.txt` - Python dependencies
- `post-surgy-instruction-builder-agent/instruction_builder_agent.py` - Core agent logic
- `post-surgy-instruction-builder-agent/prompts_instructions.py` - System prompts
- `post-surgy-instruction-builder-agent/agent_agentcore.py` - AgentCore entrypoint
- `post-surgy-instruction-builder-agent/test_payloads.json` - Test data
- `post-surgy-instruction-builder-agent/Dockerfile.agentcore` - Docker configuration
- `post-surgy-instruction-builder-agent/.bedrock_agentcore.yaml` - AgentCore config
- `post-surgy-instruction-builder-agent/deploy_agentcore.py` - Deployment script
- `post-surgy-instruction-builder-agent/invoke_agent.py` - Invocation script
- `post-surgy-instruction-builder-agent/env.example` - Environment variable template

### Files to Modify
- `app/services/agent_instruction_builder_service.rb` - Update to use new agent ARN
- `.env.example` or environment config - Add new ARN variable

### Files to Delete
- None

### Dependencies Map

```
post-surgy-instruction-builder-agent
  ├── Strands Agent (strands-agents library)
  │   ├── InstructionResponse (Pydantic model)
  │   ├── System Prompts (prompts_instructions.py)
  │   └── Agent Logic (instruction_builder_agent.py)
  ├── Bedrock AgentCore Runtime
  │   ├── Entrypoint (agent_agentcore.py)
  │   └── Configuration (.bedrock_agentcore.yaml)
  └── Docker Container
      └── Dockerfile.agentcore

Rails Application
  └── AgentInstructionBuilderService
      ├── Uses BEDROCK_INSTRUCTION_BUILDER_AGENT_RUNTIME_ARN
      └── Invokes agent with instruction_generation/adjustment payloads
```

### Affected Components

- **New Agent Project**: Completely new codebase following patient agent pattern
- **Rails Service**: Minor update to use new ARN environment variable
- **AWS Bedrock**: New agent runtime deployment (separate from patient agent)
- **Environment Configuration**: New ARN variable needed

### Test Impact

- **Agent Testing**: Test payloads included in project for manual testing
- **Integration Testing**: Rails service already handles response parsing, should work with new agent
- **Deployment Testing**: Use deployment script to verify agent works in AgentCore

## Risk Assessment

### High Risk Areas
- **Agent Prompt Quality**: System prompts need to be carefully crafted to generate accurate, safe medical instructions. Mitigation: Review prompts with medical professionals, include safety guidelines, test extensively.
- **Response Format Compatibility**: Agent must return exact format Rails expects (`instructions` and `reasoning` fields). Mitigation: Use structured output with Pydantic, match field names exactly.

### Medium Risk Areas
- **Deployment Configuration**: AgentCore configuration must match AWS account and permissions. Mitigation: Use same configuration pattern as patient agent, verify ARN and permissions.
- **Context Handling**: Agent must handle all context fields Rails sends. Mitigation: Test with various procedure types and contexts, handle missing fields gracefully.

### Breaking Changes
- **Environment Variable**: New `BEDROCK_INSTRUCTION_BUILDER_AGENT_RUNTIME_ARN` required. Existing `BEDROCK_AGENT_RUNTIME_ARN` remains for patient communication.
- **No Breaking Changes**: Rails service already structured to handle different ARNs, just needs environment variable update.

### Rollback Plan
- Keep old `BEDROCK_AGENT_RUNTIME_ARN` unchanged (used for patient communication)
- New agent is additive - can disable by not setting new ARN variable
- Rails service will fail gracefully if ARN not configured

## Implementation Roadmap

### Phase 1: Project Structure and Core Agent
- [ ] Task 1.1: Create Project Directory Structure
- [ ] Task 1.2: Create Requirements and Dependencies
- [ ] Task 1.3: Create Instruction Response Pydantic Model
- [ ] Task 1.4: Create System Prompts for Instruction Building
- **Checkpoint**: Project structure matches patient agent, models and prompts defined

### Phase 2: Agent Implementation
- [ ] Task 2.1: Implement Instruction Builder Agent Core Logic
- [ ] Task 2.2: Implement AgentCore Entrypoint
- [ ] Task 2.3: Create Test Payloads
- **Checkpoint**: Agent can process both instruction_generation and instruction_adjustment types locally

### Phase 3: Deployment Configuration
- [ ] Task 3.1: Create Dockerfile for AgentCore
- [ ] Task 3.2: Create Bedrock AgentCore Configuration
- [ ] Task 3.3: Create Deployment Script
- [ ] Task 3.4: Create Invocation Script
- **Checkpoint**: Agent can be deployed to AgentCore and invoked successfully

### Phase 4: Integration with Rails
- [ ] Task 4.1: Update Rails Environment Variables
- [ ] Task 4.2: Update AgentInstructionBuilderService to Use New ARN
- **Checkpoint**: Rails service can invoke new agent and receive responses correctly

## Notes and Considerations

- **Agent Separation**: Instruction builder agent is separate from patient communication agent. This maintains clear separation of concerns and allows different agent configurations.
- **Structured Output**: Use Pydantic models to ensure consistent response format. Field names must match what Rails expects: `instructions` and `reasoning`.
- **Prompt Engineering**: System prompts are critical for instruction quality. Should include:
  - Medical safety guidelines
  - Procedure-specific considerations
  - Days post-op relevance
  - Patient-friendly language requirements
  - What to include (medications, activity restrictions, warning signs, follow-up)
  - What to exclude (diagnosis, treatment recommendations beyond instructions)
- **Context Handling**: Agent should handle all context fields from Rails:
  - `procedure_id`, `procedure_type`, `procedure_status`, `perform_at`
  - `days_post_op`, `patient_id`, `patient_name`, `doctor_name`
  - `procedure_history` (for instruction_generation)
  - `current_instructions` (for instruction_adjustment)
  - `message` (for instruction_adjustment - doctor/nurse feedback)
- **Error Handling**: Agent should return structured error responses that Rails can handle gracefully.
- **Testing**: Use test payloads to verify agent behavior before deployment. Test with various procedure types and adjustment scenarios.
- **Deployment**: Follow same deployment process as patient agent. Use `.bedrock_agentcore.yaml` for configuration management.
- **Observability**: Agent includes OpenTelemetry instrumentation for monitoring and debugging.

## Related Exploration Documents

- Reference implementation: `/Users/haris.pandzic/projects/post-surgy-patient-agent/`
- Rails service: `app/services/agent_instruction_builder_service.rb`
