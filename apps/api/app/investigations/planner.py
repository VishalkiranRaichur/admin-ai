from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Protocol

from app.investigations.errors import PlanValidationError
from app.investigations.registry import ENABLED_TOOLS, resolve_metric
from app.schemas.investigation import (
    CalculateMetricChangeInput,
    InvestigationIntent,
    InvestigationIntentType,
    InvestigationPlan,
    InvestigationPlanStep,
    InvestigationToolCall,
    InvestigationToolKind,
    QueryMetricSeriesInput,
    QueryRelatedRecordsInput,
    RankEntityContributionsInput,
    SemanticDocumentSearchInput,
    TraverseRelationshipsInput,
)
from app.services.structured_response import parse_structured_response


class PlannerGateway(Protocol):
    async def create_plan(self, question: str) -> InvestigationPlan: ...


class ModelPlannerGateway:
    async def create_plan(self, question: str) -> InvestigationPlan:
        return await parse_structured_response(
            response_type=InvestigationPlan,
            instructions=(
                "Create one bounded business investigation plan. Use only the supplied schema and "
                "allowlisted tools. Never emit SQL. Use at most eight sequential steps."
            ),
            input_text=question,
        )


class DeterministicPlannerGateway:
    """Deterministic adapter used by CI and the ORION demo evaluation."""

    async def create_plan(self, question: str) -> InvestigationPlan:
        lowered = question.lower()
        if "revenue" not in lowered or "july" not in lowered:
            raise PlanValidationError(
                "The deterministic planner only supports the July revenue demo"
            )
        metric = "recognized_revenue_usd"
        steps = [
            InvestigationPlanStep(
                sequence=1,
                description="Retrieve June and July revenue by customer",
                tool_call=InvestigationToolCall(
                    tool=InvestigationToolKind.QUERY_METRIC_SERIES,
                    arguments=QueryMetricSeriesInput(
                        metric_key=metric,
                        period_start=date(2026, 6, 1),
                        period_end=date(2026, 7, 31),
                    ),
                ),
            ),
            InvestigationPlanStep(
                sequence=2,
                description="Calculate total revenue change",
                depends_on=[1],
                tool_call=InvestigationToolCall(
                    tool=InvestigationToolKind.CALCULATE_METRIC_CHANGE,
                    arguments=CalculateMetricChangeInput(
                        current_step=1,
                        current_period_start=date(2026, 7, 1),
                        comparison_period_start=date(2026, 6, 1),
                    ),
                ),
            ),
            InvestigationPlanStep(
                sequence=3,
                description="Rank customer contribution to the decline",
                depends_on=[1],
                tool_call=InvestigationToolCall(
                    tool=InvestigationToolKind.RANK_ENTITY_CONTRIBUTIONS,
                    arguments=RankEntityContributionsInput(
                        metric_step=1,
                        current_period_start=date(2026, 7, 1),
                        comparison_period_start=date(2026, 6, 1),
                    ),
                ),
            ),
            InvestigationPlanStep(
                sequence=4,
                description="Retrieve records for the largest contributor",
                required=False,
                depends_on=[3],
                tool_call=InvestigationToolCall(
                    tool=InvestigationToolKind.QUERY_RELATED_RECORDS,
                    arguments=QueryRelatedRecordsInput(
                        entity_selector="top_contributor",
                        start=datetime(2026, 5, 1, tzinfo=UTC),
                        end=datetime(2026, 7, 31, 23, 59, tzinfo=UTC),
                    ),
                ),
            ),
            InvestigationPlanStep(
                sequence=5,
                description="Traverse relationships for the largest contributor",
                required=False,
                depends_on=[3],
                tool_call=InvestigationToolCall(
                    tool=InvestigationToolKind.TRAVERSE_RELATIONSHIPS,
                    arguments=TraverseRelationshipsInput(
                        entity_selector="top_contributor", depth=2
                    ),
                ),
            ),
            InvestigationPlanStep(
                sequence=6,
                description="Search supporting documents",
                required=False,
                depends_on=[3],
                tool_call=InvestigationToolCall(
                    tool=InvestigationToolKind.SEMANTIC_DOCUMENT_SEARCH,
                    arguments=SemanticDocumentSearchInput(
                        query="Northstar renewal export failures remediation delay",
                        entity_selector="top_contributor",
                        limit=10,
                    ),
                ),
            ),
        ]
        return InvestigationPlan(
            intent=InvestigationIntent(
                kind=InvestigationIntentType.CAUSAL_ANALYSIS,
                metric=metric,
                organization_scope="company-wide",
                assumptions=["The latest available July (July 2026) was intended."],
            ),
            steps=steps,
            created_at=datetime.now(UTC),
        )


def canonicalize_plan(plan: InvestigationPlan) -> InvestigationPlan:
    if len(plan.steps) > 8:
        raise PlanValidationError("Plans may contain at most eight steps")
    if not plan.intent.metric:
        raise PlanValidationError(
            "Phase 2 supports recognized-revenue metric investigations only"
        )
    plan.intent.metric = resolve_metric(plan.intent.metric)
    tools_by_sequence = {step.sequence: step.tool_call.tool for step in plan.steps}
    for step in plan.steps:
        if step.tool_call.tool not in ENABLED_TOOLS:
            raise PlanValidationError(f"Unknown tool: {step.tool_call.tool}")
        if step.tool_call.tool == InvestigationToolKind.QUERY_METRIC_SERIES:
            arguments = step.tool_call.arguments
            assert isinstance(arguments, QueryMetricSeriesInput)
            arguments.metric_key = resolve_metric(arguments.metric_key)

        referenced_steps: list[tuple[int, InvestigationToolKind]] = []
        if step.tool_call.tool == InvestigationToolKind.CALCULATE_METRIC_CHANGE:
            arguments = step.tool_call.arguments
            assert isinstance(arguments, CalculateMetricChangeInput)
            referenced_steps.append(
                (arguments.current_step, InvestigationToolKind.QUERY_METRIC_SERIES)
            )
            if arguments.comparison_step:
                referenced_steps.append(
                    (arguments.comparison_step, InvestigationToolKind.QUERY_METRIC_SERIES)
                )
        elif step.tool_call.tool == InvestigationToolKind.RANK_ENTITY_CONTRIBUTIONS:
            arguments = step.tool_call.arguments
            assert isinstance(arguments, RankEntityContributionsInput)
            referenced_steps.append(
                (arguments.metric_step, InvestigationToolKind.QUERY_METRIC_SERIES)
            )

        for referenced_sequence, expected_tool in referenced_steps:
            if referenced_sequence >= step.sequence:
                raise PlanValidationError("Tool inputs must reference earlier plan steps")
            if tools_by_sequence.get(referenced_sequence) != expected_tool:
                raise PlanValidationError(
                    f"Step {referenced_sequence} must use {expected_tool.value}"
                )
            if referenced_sequence not in step.depends_on:
                raise PlanValidationError(
                    f"Step {step.sequence} must depend on referenced step {referenced_sequence}"
                )

        selector = getattr(step.tool_call.arguments, "entity_selector", None)
        if selector is not None:
            ranking_steps = [
                sequence
                for sequence, tool in tools_by_sequence.items()
                if sequence < step.sequence
                and tool == InvestigationToolKind.RANK_ENTITY_CONTRIBUTIONS
            ]
            if not ranking_steps:
                raise PlanValidationError(
                    "Dynamic entity selectors require an earlier ranking step"
                )
            if not any(sequence in step.depends_on for sequence in ranking_steps):
                raise PlanValidationError(
                    "Dynamic entity selectors must depend on an earlier ranking step"
                )

    present = {step.tool_call.tool for step in plan.steps if step.required}
    required = {
        InvestigationToolKind.QUERY_METRIC_SERIES,
        InvestigationToolKind.CALCULATE_METRIC_CHANGE,
        InvestigationToolKind.RANK_ENTITY_CONTRIBUTIONS,
    }
    missing = required - present
    if missing:
        names = ", ".join(sorted(item.value for item in missing))
        raise PlanValidationError(f"Metric plan is missing required steps: {names}")
    return InvestigationPlan.model_validate(plan.model_dump())
