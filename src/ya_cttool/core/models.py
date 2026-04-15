from enum import Enum
from dataclasses import dataclass, field

from marshmallow import Schema, fields, post_load, ValidationError
from marshmallow_dataclass import class_schema
from marshmallow_enum import EnumField
import angr

class HexInteger(fields.Field):
    """
    Marshmallow field that serializes int -> hex string
    and deserializes hex string -> int.
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if not isinstance(value, int):
            raise ValidationError("Expected int for HexInteger")
        return hex(value)  # e.g. "0x1a2b"

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value, 16)  # accepts "0x1a2b" or "1a2b"
            except ValueError as e:
                raise ValidationError("Invalid hex string") from e
        raise ValidationError("Expected hex string for HexInteger")

@dataclass(frozen=True)
class MultiStatesBasicBlock:
    """
    A basic block associated to a list of possible program states.
    """

    states: list[angr.SimState] = field(default_factory=list)


@dataclass(frozen=True)
class ConsolidatedBasicBlock:
    """
    A basic block for which the possible program states were merged into a single over-approximation program state.
    """

    state: angr.SimState


BasicBlock = MultiStatesBasicBlock | ConsolidatedBasicBlock


class EventType(str, Enum):
    Branching = "branching"
    Memory = "memory"


class Color(str, Enum):
    Red = "red"
    Orange = "orange"
    Green = "green"


@dataclass(frozen=True)
class AnalysisEvent:
    """
    A memory access or a conditional branching encountered during the analysis.

    Attributes:
        program_point: the IP where the event happened
        type: memory access or conditional branching
        status: status (red / orange / green / concrete value) of the address of the memory access or of the condition of the
            branching
    """
    program_point: int
    type: EventType
    status: Color | int


@dataclass
class Metadata:
    cfg: dict
    exploration_time: float

@dataclass(frozen=True, eq=True)
class Source:
    file: str
    line: int
    fullpath: str
    funcname: str

@dataclass(frozen=True, eq=True)
class ResultItem:
    """
    A CT violation discovered by the analysis
    """

    binary_file: str
    binary_address: int = field(
        metadata={"marshmallow_field": HexInteger()}
    )
    type: EventType = field(
        metadata={"marshmallow_field": EnumField(EventType, by_value=True)}
    )
    color: Color = field(
        metadata={"marshmallow_field": EnumField(Color, by_value=True)}
    )
    source: Source | None

# class ResultItemSchema(Schema):
#     source_file = fields.String()
#     line = fields.Int()
#     type = fields.Enum(EventType, by_value=True)
#     color = fields.Enum(Color, by_value=True)

#     @post_load
#     def make_resultItem(self, data, **kwargd):
#         return ResultItem(**data)


@dataclass(frozen=True, eq=True)
class StatementResult:
    """"""

    src_file: str
    src_lnb: int
    src_lines: tuple[tuple[int, str],...]
    src_vars: tuple[tuple[str, str],...]

    def display(self):
        print("-" * 59)
        for item in self.src_vars:
            location_str = item[0].ljust(20)
            print(f"{location_str} : {item[1]}")
        for item in self.src_lines:
            print(f"[{self.src_file}:{item[0]}] {item[1]}", end="")
        if len(self.src_lines) == 0:
            print(f"{self.src_file}:{self.src_lnb}")
        print()


# class StatementResultSchema(Schema):
#     src_file = fields.String()
#     src_lnb = fields.Integer()
#     src_lines = fields.List(fields.Tuple([fields.Integer(), fields.String()]))
#     src_vars = fields.List(fields.Tuple([fields.String(), fields.String()]))

#     @post_load
#     def make_blockStepResult(self, data, **kwargd):
#         return ResultItem(**data)

SourceSchema = class_schema(Source)()
StatementResultSchema = class_schema(StatementResult)()
ResultItemSchema = class_schema(ResultItem)()