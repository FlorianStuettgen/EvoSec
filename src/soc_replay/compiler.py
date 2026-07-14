from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import INDEX_FIELDS
from .models import Aggregate, Condition, Event, Rule, Scenario
from .operators import OperatorFn, get_operator
from .serialization import digest_object, to_primitive


@dataclass(frozen=True, slots=True)
class FieldAccessor:
    field: str
    path: tuple[str, ...]

    @classmethod
    def compile(cls, field: str) -> FieldAccessor:
        return cls(field=field, path=tuple(field.split(".")))

    def __call__(self, event: Event) -> Any:
        return event.value_path(self.path)


@dataclass(frozen=True, slots=True)
class CompiledCondition:
    source: Condition
    accessor: FieldAccessor
    evaluator: OperatorFn

    def matches(self, event: Event) -> bool:
        return self.evaluator(self.accessor(event), self.source.value)


@dataclass(frozen=True, slots=True)
class CandidateSelector:
    field: str
    value: str
    mode: str

    def to_dict(self) -> dict[str, str]:
        return {"field": self.field, "value": self.value, "mode": self.mode}


@dataclass(frozen=True, slots=True)
class CompiledAggregate:
    source: Aggregate
    group_accessors: tuple[FieldAccessor, ...]
    distinct_accessor: FieldAccessor | None


@dataclass(frozen=True, slots=True)
class CompiledRule:
    source: Rule
    conditions: tuple[CompiledCondition, ...]
    aggregate: CompiledAggregate | None
    candidate_selectors: tuple[CandidateSelector, ...]
    fingerprint: str

    def matches(self, event: Event) -> bool:
        return all(condition.matches(event) for condition in self.conditions)


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    scenario: Scenario
    rules: tuple[CompiledRule, ...]
    fingerprint: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario.scenario_id,
            "fingerprint": self.fingerprint,
            "rules": [
                {
                    "id": rule.source.rule_id,
                    "fingerprint": rule.fingerprint,
                    "candidate_selectors": [selector.to_dict() for selector in rule.candidate_selectors],
                }
                for rule in self.rules
            ],
        }


def _candidate_selectors(conditions: tuple[Condition, ...]) -> tuple[CandidateSelector, ...]:
    selectors: list[CandidateSelector] = []
    seen: set[tuple[str, str, str]] = set()
    for condition in conditions:
        selector: CandidateSelector | None = None
        if condition.field in INDEX_FIELDS and condition.operator == "eq" and isinstance(condition.value, str):
            selector = CandidateSelector(condition.field, condition.value, "eq")
        elif condition.field == "tags" and condition.operator == "contains" and isinstance(condition.value, str):
            selector = CandidateSelector("tags", condition.value, "contains")
        if selector is None:
            continue
        key = (selector.field, selector.value, selector.mode)
        if key not in seen:
            selectors.append(selector)
            seen.add(key)
    return tuple(selectors)


def compile_rule(rule: Rule) -> CompiledRule:
    compiled_conditions = tuple(
        CompiledCondition(condition, FieldAccessor.compile(condition.field), get_operator(condition.operator).evaluate)
        for condition in rule.conditions
    )
    compiled_aggregate = None
    if rule.aggregate is not None:
        compiled_aggregate = CompiledAggregate(
            source=rule.aggregate,
            group_accessors=tuple(FieldAccessor.compile(field) for field in rule.aggregate.group_by),
            distinct_accessor=FieldAccessor.compile(rule.aggregate.distinct_field)
            if rule.aggregate.distinct_field
            else None,
        )
    semantic_payload = {
        "id": rule.rule_id,
        "name": rule.name,
        "severity": rule.severity,
        "description": rule.description,
        "conditions": [
            {"field": condition.field, "operator": condition.operator, "value": to_primitive(condition.value)}
            for condition in rule.conditions
        ],
        "aggregate": None
        if rule.aggregate is None
        else {
            "group_by": list(rule.aggregate.group_by),
            "count_gte": rule.aggregate.count_gte,
            "within_seconds": rule.aggregate.within_seconds,
            "distinct_field": rule.aggregate.distinct_field,
            "distinct_gte": rule.aggregate.distinct_gte,
            "window_policy": rule.aggregate.window_policy,
        },
        "response": {
            "action": rule.response.action,
            "description": rule.response.description,
            "mode": rule.response.mode,
        },
    }
    return CompiledRule(
        source=rule,
        conditions=compiled_conditions,
        aggregate=compiled_aggregate,
        candidate_selectors=_candidate_selectors(rule.conditions),
        fingerprint=digest_object(semantic_payload),
    )


def compile_scenario(scenario: Scenario) -> ExecutionPlan:
    rules = tuple(compile_rule(rule) for rule in scenario.rules)
    fingerprint = digest_object(
        {
            "scenario_schema_version": scenario.schema_version,
            "scenario_id": scenario.scenario_id,
            "rules": [rule.fingerprint for rule in rules],
        }
    )
    return ExecutionPlan(scenario=scenario, rules=rules, fingerprint=fingerprint)
