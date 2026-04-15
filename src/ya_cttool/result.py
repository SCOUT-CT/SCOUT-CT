import time
from typing_extensions import Any

import claripy

from .core.models import BasicBlock, ResultItem, StatementResult
from .core.result import generate_constant_time_analysis_result

def compute_results(explored_states: dict[tuple[int], BasicBlock]) -> tuple[dict[str, Any],list[ResultItem], list[StatementResult]]:
    """
    Displays the result of the static taint analysis.

    Checks if the program contains memory accesses with an orange or red tainted address, or branching instructions with an orange
    or red tainted condition.
    """
    claripy.simplifications._all_simplifiers = {} # type: ignore
    start = time.time()
    res_items, block_step_res = generate_constant_time_analysis_result(explored_states)
    end = time.time()
    metadata: dict[str, Any] = {
        "results_gen_time": end - start
    }
    return metadata, res_items, block_step_res

