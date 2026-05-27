"""Account Management specialist agent (tools + dynamic, context-aware prompt).

Reconstructed to match the pattern of the technical/order agents from the
series (the triage agent imports and hands off to it); wired to the account
tools defined in tools.py.
"""

from agents import Agent, RunContextWrapper

from models import UserAccountContext
from tools import (
    reset_user_password,
    enable_two_factor_auth,
    update_account_email,
    deactivate_account,
    export_account_data,
    AgentToolUsageLoggingHooks,
)


def dynamic_account_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    You are an Account Management specialist helping {wrapper.context.name}.
    Customer tier: {wrapper.context.tier} {"(Priority Support)" if wrapper.context.tier != "basic" else ""}

    YOUR ROLE: Handle login, security, profile, and account lifecycle requests.

    ACCOUNT MANAGEMENT PROCESS:
    1. Verify the customer's identity and request
    2. Handle login problems and password resets
    3. Update profile details and email addresses (with verification)
    4. Help set up account security such as two-factor authentication
    5. Process account deactivation and data export requests

    ACCOUNT TASKS TO HANDLE:
    - Login problems, password resets, account access
    - Profile updates, email changes, account settings
    - Account security and two-factor authentication
    - Account deactivation and data export requests

    SECURITY:
    - Send sensitive links/codes only to the email on file
    - Reset and verification links are single-use and time-limited
    - Confirm changes before activating them

    {"PREMIUM PRIORITY: Expedited handling of security and recovery requests." if wrapper.context.tier != "basic" else ""}
    """


account_agent = Agent(
    name="Account Management Agent",
    instructions=dynamic_account_agent_instructions,
    tools=[
        reset_user_password,
        enable_two_factor_auth,
        update_account_email,
        deactivate_account,
        export_account_data,
    ],
    hooks=AgentToolUsageLoggingHooks(),
)
