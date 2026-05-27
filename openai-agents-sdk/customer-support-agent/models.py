"""Pydantic models: the shared run context and the guardrail/handoff schemas."""

from typing import Optional

from pydantic import BaseModel


class UserAccountContext(BaseModel):
    """Per-run context passed to every agent, tool, and guardrail.

    The Agents SDK injects this object (via RunContextWrapper) so tools and
    dynamic instructions can read who the customer is and tailor behavior.
    """

    customer_id: int
    name: str
    tier: str = "basic"  # basic | premium | enterprise
    email: Optional[str] = None

    # Lightweight in-context state collected during a run.
    troubleshooting_steps: list[str] = []

    def is_premium_customer(self) -> bool:
        return self.tier != "basic"

    def add_troubleshooting_step(self, step: str) -> None:
        self.troubleshooting_steps.append(step)


class InputGuardRailOutput(BaseModel):
    """Structured output of the input guardrail agent."""

    is_off_topic: bool
    reason: str


class HandoffData(BaseModel):
    """Structured payload the triage agent emits when handing off."""

    to_agent_name: str
    issue_type: str
    issue_description: str
    reason: str


class TechnicalOutputGuardRailOutput(BaseModel):
    """Structured output of the technical-agent output guardrail."""

    contains_off_topic: bool
    contains_billing_data: bool
    contains_account_data: bool
    reason: str
