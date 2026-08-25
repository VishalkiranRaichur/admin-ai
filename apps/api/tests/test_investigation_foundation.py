import uuid

import pytest
from pydantic import ValidationError

from app.capabilities import CAPABILITY_STATES, Capability, CapabilityState
from app.schemas.investigation import (
    ExecutiveBrief,
    ExecutiveBriefConfidence,
    ExecutiveBriefConfidenceLevel,
    ExecutiveBriefEvidence,
    InvestigationIntent,
    InvestigationIntentType,
    InvestigationPlan,
    InvestigationPlanStep,
    InvestigationToolCall,
    InvestigationToolKind,
    SupportedBriefStatement,
    validate_executive_brief_references,
)


def test_investigate_is_active_during_phase_two() -> None:
    assert CAPABILITY_STATES == {
        Capability.ASK: CapabilityState.ACTIVE,
        Capability.INVESTIGATE: CapabilityState.ACTIVE,
        Capability.WATCH: CapabilityState.INACTIVE,
        Capability.ACT: CapabilityState.INACTIVE,
    }


def test_investigation_plan_is_bounded_to_eight_steps() -> None:
    intent = InvestigationIntent(kind=InvestigationIntentType.CAUSAL_ANALYSIS)
    steps = [
        InvestigationPlanStep(
            sequence=index,
            description=f"Step {index}",
            tool_call=InvestigationToolCall(tool=InvestigationToolKind.SEMANTIC_DOCUMENT_SEARCH),
        )
        for index in range(1, 10)
    ]

    with pytest.raises(ValidationError):
        InvestigationPlan(intent=intent, steps=steps)


def test_executive_brief_references_are_validated() -> None:
    claim_id = uuid.uuid4()
    evidence_id = uuid.uuid4()
    brief = ExecutiveBrief(
        what_happened=SupportedBriefStatement(
            text="Revenue declined in July.", claim_ids=[claim_id]
        ),
        confidence=ExecutiveBriefConfidence(
            score=0.8,
            level=ExecutiveBriefConfidenceLevel.HIGH,
            rationale="The measured change is supported by monthly observations.",
        ),
        key_evidence=[
            ExecutiveBriefEvidence(
                evidence_id=evidence_id,
                label="July revenue observation",
                claim_ids=[claim_id],
            )
        ],
    )

    validate_executive_brief_references(
        brief,
        valid_claim_ids={claim_id},
        valid_evidence_ids={evidence_id},
    )

    with pytest.raises(ValueError, match="Unknown Executive Brief evidence ID"):
        validate_executive_brief_references(
            brief,
            valid_claim_ids={claim_id},
            valid_evidence_ids=set(),
        )
