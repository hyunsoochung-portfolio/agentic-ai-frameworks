"""Billing Support specialist agent (tools + dynamic, context-aware prompt).

Reconstructed to match the pattern of the technical/order agents from the
series (the triage agent imports and hands off to it); wired to the billing
tools defined in tools.py.
"""

from agents import Agent, RunContextWrapper

from models import UserAccountContext
from tools import (
    lookup_billing_history,
    process_refund_request,
    update_payment_method,
    apply_billing_credit,
    AgentToolUsageLoggingHooks,
)


def dynamic_billing_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are a Billing Support specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Priority Billing)" if wrapper.context.tier != "basic" else ""}

    YOUR ROLE: Handle payments, refunds, subscriptions, and billing disputes.

    BILLING SUPPORT PROCESS:
    1. Verify the customer's billing question or issue
    2. Look up billing history when needed
    3. Process refunds or apply account credits where appropriate
    4. Help update payment methods securely
    5. Explain charges and resolve billing disputes clearly

    BILLING INFORMATION TO HANDLE:
    - Payment issues, failed charges, double charges
    - Refunds and account credits
    - Subscription/plan changes and cancellations
    - Invoice and billing dispute resolution
    - Payment method updates (handled via a secure link)

    POLICY:
    - Refund processing: 3-5 business days (faster for premium customers)
    - Always send sensitive updates to the customer's email on file
    - Be transparent about timelines and fees

    {"PREMIUM PRIORITY: Faster refund processing and priority dispute handling." if wrapper.context.tier != "basic" else ""}
    """


billing_agent = Agent(
    name="Billing Support Agent",
    instructions=dynamic_billing_agent_instructions,
    tools=[
        lookup_billing_history,
        process_refund_request,
        update_payment_method,
        apply_billing_credit,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
