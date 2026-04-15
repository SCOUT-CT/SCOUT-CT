from enum import Enum

from .core.models import BasicBlock


class TimeoutException(Exception):
    ...


class AnalysisInterruptKind(Enum):
    Timeout = 0
    TaintedMemoryWrite = 1
    MaxConsolidationThreshold = 2
    KeyboardInterrupt = 3
    NoInterrupt = 4

class AnalysisInterruptError(Exception):

    def __init__(self, kind: AnalysisInterruptKind, dicovered_blocks: dict[tuple[int], BasicBlock]):            
        super().__init__(f"Analysis interrupt error of kind {kind.name}")
        self.discovered_blocks = dicovered_blocks
        self.kind = kind