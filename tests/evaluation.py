from dataclasses import dataclass, asdict, field
from json import JSONEncoder
from typing import Any, Mapping
from marshmallow import Schema, fields, post_load, pre_dump
from marshmallow_dataclass import class_schema
from marshmallow_enum import EnumField

from ya_cttool.core.models import EventType, Color


@dataclass(frozen=True, eq=True)
class TestingResultItem:
    source_file: str
    line: int
    type: EventType = field(
        metadata={"marshmallow_field": EnumField(EventType, by_value=True)}
    )
    color: Color = field(
        metadata={"marshmallow_field": EnumField(Color, by_value=True)}
    )


TestingResultItemSchema = class_schema(TestingResultItem)()


class DataclassJSONEncoder(JSONEncoder):
    def default(self, o):
        if hasattr(o, "__dataclass_fields__"):
            return asdict(o)
        return super().default(o)


@dataclass
class Metrics:
    tp: int
    fp: int
    fn: int


class MetricsSchema(Schema):
    tp = fields.Int(required=True)
    fp = fields.Int(required=True)
    fn = fields.Int(required=True)

    @post_load
    def make_metrics(self, data, **kwargd):
        return Metrics(**data)

    class Meta:
        json_module = DataclassJSONEncoder


class MetricsField(fields.Field[Metrics]):
    def _deserialize(
        self, value: Any, attr: str | None, data: Mapping[str, Any] | None, **kwargs
    ) -> Metrics:
        return super()._deserialize(value, attr, data, **kwargs)

    def _serialize(
        self, value: Metrics | None, attr: str | None, obj: Any, **kwargs
    ) -> Any:
        return super()._serialize(value, attr, obj, **kwargs)


@dataclass
class EvalSummary:
    test_passed: bool
    metrics: Metrics


class EvalSummarySchema(Schema):
    test_passed = fields.Boolean(required=True)
    metrics = MetricsField(required=True)

    class Meta:
        json_module = DataclassJSONEncoder

    @post_load
    def make_resultSummary(self, data, **kwargd):
        return EvalSummary(**data)

    @pre_dump
    def convert_to_dict(self, obj, **kwargs):
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        return obj


@dataclass
class ComparisonResult:
    tp: list[TestingResultItem]
    fp: list[TestingResultItem]
    fn: list[TestingResultItem]


def evaluate(
    results: list[TestingResultItem], expected: list[TestingResultItem]
) -> tuple[ComparisonResult, Metrics]:
   
    res_set = set(results)
    exp_set = set(expected)

    tp = exp_set.intersection(res_set)
    fp = res_set - exp_set
    fn = exp_set - res_set

    return ComparisonResult(list(tp), list(fp), list(fn)), Metrics(
        len(tp), len(fp), len(fn)
    )
