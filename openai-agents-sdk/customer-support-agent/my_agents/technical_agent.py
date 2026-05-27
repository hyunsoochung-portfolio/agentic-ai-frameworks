"""Technical Support specialist agent.

Demonstrates an OUTPUT guardrail: after the agent generates a reply, a dedicated
guardrail agent inspects it and trips a wire if the technical agent leaked
billing / order / account content outside its role.
"""

from agents import (
    Agent,
    RunContextWrapper,
    output_guardrail,
    Runner,
    GuardrailFunctionOutput,
)

from models import UserAccountContext, TechnicalOutputGuardRailOutput
from tools import (
    run_diagnostic_check,
    provide_troubleshooting_steps,
    escalate_to_engineering,
    AgentToolUsageLoggingHooks,
)


technical_output_guardrail_agent = Agent(
    name="Technical Support Guardrail",
    instructions="""
    Analyze the technical support response to check if it inappropriately contains:

    - Billing information (payments, refunds, charges, subscriptions)
    - Order information (shipping, tracking, delivery, returns)
    - Account management info (passwords, email changes, account settings)

    Technical agents should ONLY provide technical troubleshooting, diagnostics, and product support.
    Return true for any field that contains inappropriate content for a technical support response.
    """,
    output_type=TechnicalOutputGuardRailOutput,
)


@output_guardrail
async def technical_output_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent,
    output: str,
):
    result = await Runner.run(
        technical_output_guardrail_agent,
        output,
        context=wrapper.context,
    )
    validation = result.final_output
    triggered = (
        validation.contains_off_topic
        or validation.contains_billing_data
        or validation.contains_account_data
    )
    return GuardrailFunctionOutput(
        output_info=validation,
        tripwire_triggered=triggered,
    )


def dynamic_technical_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are a Technical Support specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Premium Support)" if wrapper.context.tier != "basic" else ""}

    YOUR ROLE: Solve technical issues with our products and services.

    TECHNICAL SUPPORT PROCESS:
    1. Gather specific details about the technical issue
    2. Ask for error messages, steps to reproduce, system info
    3. Provide step-by-step troubleshooting solutions
    4. Test solutions with the customer
    5. Escalate to engineering if needed (especially for premium customers)

    INFORMATION TO COLLECT:
    - What product/feature they're using
    - Exact error message (if any)
    - Operating system and browser
    - Steps they took before the issue occurred
    - What they've already tried

    TROUBLESHOOTING APPROACH:
    - Start with simple solutions first
    - Be patient and explain technical steps clearly
    - Confirm each step works before moving to the next
    - Document solutions for future reference

    {"PREMIUM PRIORITY: Offer direct escalation to senior engineers if standard solutions don't work." if wrapper.context.tier != "basic" else ""}
    """


technical_agent = Agent(
    name="Technical Support Agent",
    instructions=dynamic_technical_agent_instructions,
    tools=[
        run_diagnostic_check,
        provide_troubleshooting_steps,
        escalate_to_engineering,
    ],
    hooks=AgentToolUsageLoggingHooks(),
    output_guardrails=[
        technical_output_guardrail,
    ],
)
