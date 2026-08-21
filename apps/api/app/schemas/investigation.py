from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class InvestigationStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class InvestigationStepStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class InvestigationIntentType(StrEnum):
    FACTUAL = "factual"
    CAUSAL_ANALYSIS = "causal_analysis"
    COMPARISON = "comparison"
    TREND = "trend"
    ANOMALY = "anomaly"


class ComparisonKind(StrEnum):
    PREVIOUS_PERIOD = "previous_period"
    YEAR_OVER_YEAR = "year_over_year"
    CUSTOM = "custom"


class InvestigationTimeScope(BaseModel):
    start: date | None = None
    end: date | None = None
    label: str | None = None


class InvestigationIntent(BaseModel):
    kind: InvestigationIntentType
    metric: str | None = None
    time_scope: InvestigationTimeScope | None = None
    comparison: ComparisonKind | None = None
    entity_types: list[str] = Field(default_factory=list)
    entity_ids: list[str] = Field(default_factory=list)
    organization_scope: str = "company-wide"
    assumptions: list[str] = Field(default_factory=list)


class InvestigationToolKind(StrEnum):
    QUERY_METRIC_SERIES = "query_metric_series"
    CALCULATE_METRIC_CHANGE = "calculate_metric_change"
    RANK_ENTITY_CONTRIBUTIONS = "rank_entity_contributions"
    QUERY_RELATED_RECORDS = "query_related_records"
    SEMANTIC_DOCUMENT_SEARCH = "semantic_document_search"
    TRAVERSE_RELATIONSHIPS = "traverse_relationships"


class InvestigationToolCall(BaseModel):
    tool: InvestigationToolKind
    arguments: dict[str, Any] = Field(default_factory=dict)


class InvestigationToolResult(BaseModel):
    tool: InvestigationToolKind
    evidence_ids: list[UUID] = Field(default_factory=list)
    output: dict[str, Any] = Field(default_factory=dict)


class ClaimClassification(StrEnum):
    FACT = "fact"
    DERIVED = "derived"
    HYPOTHESIS = "hypothesis"


class ClaimValidationStatus(StrEnum):
    VALIDATED = "validated"
    REJECTED = "rejected"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class EvidenceGraphNodeKind(StrEnum):
    CLAIM = "claim"
    EVIDENCE = "evidence"
    ENTITY = "entity"
    METRIC = "metric"
    CALCULATION = "calculation"
    SOURCE = "source"


class EvidenceGraphEdgeKind(StrEnum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    DERIVED_FROM = "derived_from"
    ABOUT_ENTITY = "about_entity"
    SOURCED_FROM = "sourced_from"
    INPUT_TO = "input_to"
    RELATES_TO = "relates_to"


class EvidenceGraphNode(BaseModel):
    id: str
    kind: EvidenceGraphNodeKind
    label: str
    classification: ClaimClassification | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)


class EvidenceGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: EvidenceGraphEdgeKind
    details: dict[str, Any] = Field(default_factory=dict)


class EvidenceGraph(BaseModel):
    nodes: list[EvidenceGraphNode] = Field(default_factory=list)
    edges: list[EvidenceGraphEdge] = Field(default_factory=list)


class SupportedBriefStatement(BaseModel):
    text: str = Field(min_length=1)
    claim_ids: list[UUID] = Field(min_length=1)


class ExecutiveBriefConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExecutiveBriefConfidence(BaseModel):
    score: float = Field(ge=0, le=1)
    level: ExecutiveBriefConfidenceLevel
    rationale: str = Field(min_length=1)


class ExecutiveBriefEvidence(BaseModel):
    evidence_id: UUID
    label: str = Field(min_length=1)
    claim_ids: list[UUID] = Field(default_factory=list)


class ExecutiveBriefUncertainty(BaseModel):
    text: str = Field(min_length=1)
    claim_ids: list[UUID] = Field(default_factory=list)


class ExecutiveBrief(BaseModel):
    what_happened: SupportedBriefStatement
    primary_driver: SupportedBriefStatement | None = None
    likely_explanation: SupportedBriefStatement | None = None
    confidence: ExecutiveBriefConfidence
    key_evidence: list[ExecutiveBriefEvidence] = Field(default_factory=list)
    uncertainties: list[ExecutiveBriefUncertainty] = Field(default_factory=list)
    recommended_follow_up_questions: list[str] = Field(default_factory=list)


class InvestigationPlanStep(BaseModel):
    sequence: int = Field(ge=1)
    description: str = Field(min_length=1)
    tool_call: InvestigationToolCall


class InvestigationPlan(BaseModel):
    intent: InvestigationIntent
    steps: list[InvestigationPlanStep] = Field(default_factory=list, max_length=8)
    created_at: datetime | None = None


def validate_executive_brief_references(
    brief: ExecutiveBrief,
    *,
    valid_claim_ids: set[UUID],
    valid_evidence_ids: set[UUID],
) -> None:
    referenced_claim_ids = set(brief.what_happened.claim_ids)

    for statement in (brief.primary_driver, brief.likely_explanation):
        if statement is not None:
            referenced_claim_ids.update(statement.claim_ids)

    for evidence in brief.key_evidence:
        if evidence.evidence_id not in valid_evidence_ids:
            raise ValueError(f"Unknown Executive Brief evidence ID: {evidence.evidence_id}")
        referenced_claim_ids.update(evidence.claim_ids)

    for uncertainty in brief.uncertainties:
        referenced_claim_ids.update(uncertainty.claim_ids)

    unknown_claim_ids = referenced_claim_ids - valid_claim_ids
    if unknown_claim_ids:
        unknown = ", ".join(sorted(str(claim_id) for claim_id in unknown_claim_ids))
        raise ValueError(f"Unknown Executive Brief claim IDs: {unknown}")
