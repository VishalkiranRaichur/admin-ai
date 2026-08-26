import csv
import json
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import HTTPException

import app.investigations.tools as tools_module
import app.routers.investigations as investigations_router
from app.investigations.budget import ExecutionBudget
from app.investigations.errors import ExecutionLimitError, PlanValidationError
from app.investigations.planner import DeterministicPlannerGateway, canonicalize_plan
from app.investigations.tools import ToolExecutor, decimal_string
from app.models import Investigation, InvestigationStep
from app.schemas.investigation import (
    InvestigationCreateRequest,
    InvestigationStatus,
    SemanticDocumentSearchInput,
)

DEMO_ROOT = Path(__file__).resolve().parents[3] / "demo" / "orion_company"


@pytest.mark.asyncio
async def test_deterministic_plan_is_canonical_and_bounded() -> None:
    plan = canonicalize_plan(
        await DeterministicPlannerGateway().create_plan("Why did revenue decline in July?")
    )

    assert len(plan.steps) == 6
    assert plan.intent.metric == "recognized_revenue_usd"
    assert [step.sequence for step in plan.steps] == list(range(1, 7))


@pytest.mark.asyncio
async def test_phase_two_rejects_non_metric_plans() -> None:
    plan = await DeterministicPlannerGateway().create_plan(
        "Why did revenue decline in July?"
    )
    plan.intent.metric = None

    with pytest.raises(PlanValidationError, match="recognized-revenue"):
        canonicalize_plan(plan)


@pytest.mark.asyncio
async def test_plan_rejects_forward_tool_input_references() -> None:
    plan = await DeterministicPlannerGateway().create_plan(
        "Why did revenue decline in July?"
    )
    plan.steps[1].tool_call.arguments.current_step = 3

    with pytest.raises(PlanValidationError, match="earlier plan steps"):
        canonicalize_plan(plan)


@pytest.mark.asyncio
async def test_plan_requires_declared_tool_input_dependency() -> None:
    plan = await DeterministicPlannerGateway().create_plan(
        "Why did revenue decline in July?"
    )
    plan.steps[1].depends_on = []

    with pytest.raises(PlanValidationError, match="must depend on referenced step"):
        canonicalize_plan(plan)


def test_decimal_values_are_never_converted_through_float() -> None:
    value = Decimal("9007199254740993.123400")

    assert decimal_string(value) == "9007199254740993.1234"


def test_execution_budget_rejects_calls_past_limit(monkeypatch) -> None:
    monkeypatch.setattr("app.investigations.budget.settings.investigation_max_model_calls", 1)
    budget = ExecutionBudget()

    budget.consume_model()
    with pytest.raises(ExecutionLimitError, match="model-call"):
        budget.consume_model()


def test_history_confidence_is_derived_from_valid_brief() -> None:
    score, level = investigations_router._brief_confidence(
        {
            "what_happened": {"text": "Revenue declined.", "claim_ids": [str(uuid.uuid4())]},
            "confidence": {
                "score": 0.84,
                "level": "high",
                "rationale": "Measured evidence is validated.",
            },
        }
    )

    assert score == 0.84
    assert level == "high"
    assert investigations_router._brief_confidence({"invalid": True}) == (None, None)


def test_detail_step_metadata_uses_plan_and_safe_fallbacks() -> None:
    plan = {
        "steps": [
            {
                "sequence": 2,
                "description": "Calculate the revenue change",
                "required": False,
                "depends_on": [1],
            }
        ]
    }

    assert investigations_router._step_metadata(plan, 2, "calculate_metric_change") == (
        "Calculate the revenue change",
        False,
        [1],
    )
    assert investigations_router._step_metadata(None, 1, "query_metric_series") == (
        "Query Metric Series",
        True,
        [],
    )


class EmptyScalarResult:
    def scalars(self) -> list:
        return []


class EmptyDatabase:
    async def execute(self, _statement) -> EmptyScalarResult:
        return EmptyScalarResult()


@pytest.mark.asyncio
async def test_entity_scoped_search_does_not_fall_back_to_global_corpus(monkeypatch) -> None:
    async def unexpected_search(*_args, **_kwargs):
        pytest.fail("semantic_search must not run without entity-linked documents")

    monkeypatch.setattr(tools_module, "semantic_search", unexpected_search)
    investigation_id = uuid.uuid4()
    executor = ToolExecutor(EmptyDatabase(), investigation_id, ExecutionBudget())
    step = InvestigationStep(
        id=uuid.uuid4(),
        investigation_id=investigation_id,
        sequence=1,
        tool="semantic_document_search",
    )

    result = await executor._semantic_document_search(
        step,
        SemanticDocumentSearchInput(query="renewal", entity_ids=[uuid.uuid4()]),
    )

    assert result == {"chunks": [], "evidence_ids": []}


def test_demo_fixture_matches_expected_deterministic_calculations() -> None:
    expected = json.loads((DEMO_ROOT / "expected_findings.json").read_text())
    with (DEMO_ROOT / "revenue.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    june = sum(
        Decimal(row["recognized_revenue_usd"])
        for row in rows
        if row["period_start"] == "2026-06-01"
    )
    july = sum(
        Decimal(row["recognized_revenue_usd"])
        for row in rows
        if row["period_start"] == "2026-07-01"
    )
    change = july - june
    northstar = next(
        Decimal(row["recognized_revenue_usd"])
        for row in rows
        if row["customer_id"] == "northstar" and row["period_start"] == "2026-07-01"
    ) - next(
        Decimal(row["recognized_revenue_usd"])
        for row in rows
        if row["customer_id"] == "northstar" and row["period_start"] == "2026-06-01"
    )

    assert decimal_string(june) == expected["comparison_total"]
    assert decimal_string(july) == expected["current_total"]
    assert decimal_string(change) == expected["absolute_change"]
    assert decimal_string(change / june * Decimal(100)) == expected["percentage_change"]
    assert decimal_string(northstar) == expected["primary_entity_change"]
    assert decimal_string((northstar / change * Decimal(100)).quantize(Decimal("0.0001"))) == (
        expected["contribution_percentage"]
    )


class CreateSession:
    def __init__(self) -> None:
        self.investigation: Investigation | None = None

    def add(self, investigation: Investigation) -> None:
        self.investigation = investigation

    async def commit(self) -> None:
        assert self.investigation is not None
        now = datetime.now(UTC)
        self.investigation.id = self.investigation.id or uuid.uuid4()
        self.investigation.status = self.investigation.status or InvestigationStatus.QUEUED.value
        self.investigation.created_at = self.investigation.created_at or now
        self.investigation.updated_at = self.investigation.updated_at or now

    async def refresh(self, _investigation: Investigation) -> None:
        return None


@pytest.mark.asyncio
async def test_create_investigation_enqueues_stable_task_id(monkeypatch) -> None:
    calls = []

    def send_task(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr(investigations_router.celery_client, "send_task", send_task)
    session = CreateSession()

    investigation = await investigations_router.create_investigation(
        InvestigationCreateRequest(question="Why did revenue decline in July?"), session
    )

    assert investigation.status == InvestigationStatus.QUEUED.value
    assert calls == [
        (
            ("orion.run_investigation",),
            {
                "args": [str(investigation.id)],
                "task_id": str(investigation.id),
                "queue": "investigations",
            },
        )
    ]


@pytest.mark.asyncio
async def test_create_investigation_persists_enqueue_failure(monkeypatch) -> None:
    def send_task(*_args, **_kwargs):
        raise ConnectionError("Redis unavailable")

    monkeypatch.setattr(investigations_router.celery_client, "send_task", send_task)
    session = CreateSession()

    with pytest.raises(HTTPException) as raised:
        await investigations_router.create_investigation(
            InvestigationCreateRequest(question="Why did revenue decline in July?"), session
        )

    assert raised.value.status_code == 503
    assert session.investigation is not None
    assert session.investigation.status == InvestigationStatus.FAILED.value
    assert session.investigation.failure_code == "enqueue_failed"
