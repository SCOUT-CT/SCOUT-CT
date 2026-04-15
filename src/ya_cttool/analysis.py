import math
import logging
import sys
import time


import angr
from angr.analyses.cfg import CFGBase
import claripy

from .core.models import BasicBlock, ResultItem, StatementResult, Color
from .core.tainting import build_expression_for_status
from .core.cfgexploration import propagate_taint_on_cfg
from .core.custom_engine import CustomEngine
from .config import TargetConfigManager
from .exception import AnalysisInterruptError, AnalysisInterruptKind
from .log import LOGGER_NAME
from .plugin_loading import load_hooks
from .result import compute_results

logger = logging.getLogger(LOGGER_NAME)


def do_analysis(
    binary_file_path: str,
) -> tuple[
    dict, dict, dict[tuple[int], BasicBlock], list[ResultItem], list[StatementResult]
]:
    logger.info(f"Starting analysis for {binary_file_path}")

    min_consolidation_threshold = int(
        math.log2(TargetConfigManager().get_config().min_consolidation_threshold)
    )
    max_consolidation_threshold = int(
        math.log2(TargetConfigManager().get_config().max_consolidation_threshold)
    )

    if min_consolidation_threshold == max_consolidation_threshold:
        consolidation_thresholds = [2**min_consolidation_threshold]
    else:
        # List of thresholds from `min_consolidation_threshold` to `max_consolidation_threshold`, growing exponentially.
        consolidation_thresholds = [
            2**i
            for i in range(min_consolidation_threshold, max_consolidation_threshold)
        ]

    res_metadata = {}
    analysis_metadata = {}
    explored_states = {}
    cc_violations = []
    block_step_results = []
    for consolidation_threshold in consolidation_thresholds:
        msg = f"Trying to perform analysis with consolidation threshold {consolidation_threshold}"
        logger.info(msg)
        print(msg, file=sys.stderr)

        try:
            analysis_metadata, explored_states = (
                run_analysis_with_consolidation_threshold(
                    binary_file_path, consolidation_threshold
                )
            )
        except AnalysisInterruptError as exc:
            match exc.kind:
                case AnalysisInterruptKind.TaintedMemoryWrite:
                    if consolidation_threshold == consolidation_thresholds[-1]:
                        # we are in the last loop iteration, we have exhausted all consolidation thresholds
                        logger.info(consolidation_thresholds)
                        logger.error(
                            "Memory write with tainted address happened, but we have reached max consolidation threshold."
                        )
                        raise AnalysisInterruptError(
                            kind=AnalysisInterruptKind.MaxConsolidationThreshold,
                            dicovered_blocks=exc.discovered_blocks,
                        )
                    else:
                        # we are not in the last loop iteration, we try again with a larger consolidation threshold
                        logger.info(
                            "Memory write with tainted address happened. Trying again with larger consolidation threshold."
                        )
                        continue
                case _:
                    logger.error("Analysis interrupted.")
                    raise AnalysisInterruptError(exc.kind, exc.discovered_blocks)
        except Exception as exc:
            logger.error("Error occured during the analysis.")
            logger.debug(exc)
            raise exc

        res_metadata, cc_violations, block_step_results = compute_results(
            explored_states
        )


        if any(cc_violation.color == Color.Orange for cc_violation in cc_violations):
            # We may obtain more precise results (no orange taint) with a larger threshold. Try with a larger threshold.
            msg = "Orange CC violation discovered. Trying again with larger consolidation threshold."
            logger.info(msg)
            print(msg, file=sys.stderr)
            continue
        else:
            # We obtained an ideal analysis result :
            msg = "No memory write with tainted address, and no orange CC violation"
            print(msg, file=sys.stderr)
            break

    logger.info(f"Analysis successful for {binary_file_path}")
    return (
        res_metadata,
        analysis_metadata,
        explored_states,
        cc_violations,
        block_step_results,
    )


def run_analysis_with_consolidation_threshold(
    binary_file_path: str, block_consolidation_threshold: int
) -> tuple[dict, dict[tuple[int], BasicBlock]]:
    """
    Performs a static taint analysis at machine code level, to check if the target program satisfies constant-time.

    The target program should accept two arguments. argv[1] is considered to be the secret input and argv[2] is considered to
    be the public input. The target program must have been compiled with debug symbols (-g).

    Tainting is propagated across the control-flow-graph of the target program. The concrete value of non secret dependent
    variables are tracked, in order to correctly handle memory accesses.

    Variables that depend on the secret in all possible traversals of the control-flow-graph get the *red* taint. Variables that
    depend on the secret on some traversals of the control-flow-graph get the *orange* taint.
    """
    logger.info("ANALYSIS_START")
    claripy.simplifications._all_simplifiers = {}  # type: ignore
    metadata = {}

    secret_input_expression = build_expression_for_status(Color.Red, 8)
    public_input_expression = build_expression_for_status(Color.Green, 8)

    project, entry_program_state = build_entry_program_state(
        binary_file_path,
        secret_input=secret_input_expression,
        public_input=public_input_expression,
    )

    cfg: CFGBase = project.analyses.CFG()
    nodes = cfg.model.graph.nodes()
    print(
        "CFG has %d nodes and %d edges" % (len(nodes), len(cfg.model.graph.edges())),  # type: ignore
        file=sys.stderr,
    )

    metadata["cfg"] = {
        "nodes": len(nodes),  # type: ignore
        "edges": len(cfg.model.graph.edges()),
    }
    metadata["angr_state_options"] = list(entry_program_state.options.OPTIONS.keys())

    start = time.time()
    explored_states = propagate_taint_on_cfg(
        entry_program_state, block_consolidation_threshold
    )
    end = time.time()

    metadata["exploration_time"] = end - start

    logger.info("ANALYSIS_END")

    return metadata, explored_states


def build_entry_program_state(
    binary_file_path: str,
    secret_input: claripy.ast.BV | str,
    public_input: claripy.ast.BV | str,
) -> tuple[angr.Project, angr.SimState]:
    """
    Builds an angr program state corresponding to the beginning of the execution of the program given by `binary_file_path`.

    `secret_input` is assigned to argv[1] and `public_input` is assigned to argv[2].
    """
    # `auto_load_libs=False` prevents loading of the shared libraries (e.g. glibc), which speeds up generation of the initial
    # state. We do not need the shared libraries as we analyze the code of the target program.
    # `load_debug_info=True` and `kb.dvars.load_from_dwarf()` are necessary to make angr load data from the debugging symbols of
    # the target program. This will allow us to list the C source code variables and their corresponding region in memory, in
    # order to present a user-friendly analysis result.
    angr_project = angr.Project(
        engine=CustomEngine,
        thing=binary_file_path,
        auto_load_libs=False,
        load_debug_info=True,
    )
    angr_project.kb.dvars.load_from_dwarf()

    # Usefull options ?
    # angr.options.DOWNSIZE_Z3
    # angr.options.CACHELESS_SOLVER
    # angr.options.LAZY_SOLVES
    program_state = angr_project.factory.entry_state(
        args=["", secret_input, public_input],
        add_options={
            # Prevent angr for filling padding memory space with uncontrained, untainted symbols
            angr.options.ZERO_FILL_UNCONSTRAINED_MEMORY,
            angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
            # Prevent angr from trying to handle memory accesses that have a tainted address.
            angr.options.AVOID_MULTIVALUED_READS,
            angr.options.AVOID_MULTIVALUED_WRITES,
            angr.options.LAZY_SOLVES,
            # angr.options.DOWNSIZE_Z3,
            angr.options.CACHELESS_SOLVER,
        },
    )

    # Prevents some simplifications of expressions, which add a lot of delay
    program_state.options.remove(angr.options.SIMPLIFY_MEMORY_WRITES)
    program_state.options.remove(angr.options.SIMPLIFY_REGISTER_WRITES)
    # program_state.options.remove(angr.options.SIMPLIFY_MERGED_CONSTRAINTS)

    # simplification = {SIMPLIFY_MEMORY_WRITES, SIMPLIFY_REGISTER_WRITES, SIMPLIFY_MERGED_CONSTRAINTS}

    # program_state.options.remove(*angr.options.simplification)

    urand = angr.SimPackets("red_taint")
    program_state.fs.insert("/dev/urandom", urand)  # type: ignore
    # rand = angr.SimPackets('red_taint')
    # program_state.fs.insert('/dev/random', rand)
    # angr_project.hook_symbol('hydro_random_ensure_initialized', hydro_random_ensure_initialized())

    app_config = TargetConfigManager().get_config()

    load_hooks(
        angr_project, app_config.hooks["plugin"], app_config.hooks["symbol_names"]
    )

    return angr_project, program_state
