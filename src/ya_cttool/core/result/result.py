import pathlib
import logging

from tqdm import tqdm
import angr

from .result_collector import ResultsCollector
from ..tainting import status_from_expression
from ..cfgexploration import tainting_state_in_area
from ..helpers import pc_offset
from ...common import SourceCodeLocator
from ...common import SourceCodeFilesManager
from ...config import TargetConfigManager, CommonConfig

from ...log import LOGGER_NAME
from ..models import (
    StatementResult,
    ResultItem,
    EventType,
    BasicBlock,
    MultiStatesBasicBlock,
    ConsolidatedBasicBlock,
)
from ..cfgexploration import (
    contaminate_tainted_memory_reads_with_taint,
    do_not_add_constraints_for_tainted_branches,
)


logger = logging.getLogger(LOGGER_NAME)


def generate_constant_time_analysis_result(
    explored_blocks: dict[tuple[int], BasicBlock],
) -> tuple[list[ResultItem], list[StatementResult]]:
    sources_dirs = TargetConfigManager().get_config().source_code_dirs
    SourceCodeFilesManager().find_available_source_files(sources_dirs)

    pbar = tqdm(total=len(explored_blocks), desc="Inspecting program states...", disable=CommonConfig().progress_bars_disabled)
    for block in explored_blocks.values():
        match block:
            case MultiStatesBasicBlock(states=states):
                program_states = states
            case ConsolidatedBasicBlock(state=state):
                program_states = [state]

        # logger.debug(f"len_list: {len(program_states)}")
        # program_states = set(program_states)
        # logger.debug(f"len_set: {len(program_states)}")
        logger.info(f"Nb program states : {len(program_states)}")
        # tainting_states = []
        for program_state in tqdm(
            program_states, leave=False, desc="Stepping states attached to block.",
            disable=CommonConfig().progress_bars_disabled
        ):
            # tainting_state = cfgexploration.tainting_state_at_angr_program_state(program_state)
            # tainting_states.append(tainting_state)
            program_state.options.add(angr.options.AVOID_MULTIVALUED_READS)
            program_state.options.add(angr.options.AVOID_MULTIVALUED_WRITES)
            program_state.options.add(angr.options.LAZY_SOLVES)
            program_state.options.add(angr.options.CACHELESS_SOLVER)
            # program_state.options.remove(angr.options.SIMPLIFY_MEMORY_WRITES)
            # program_state.options.remove(angr.options.SIMPLIFY_REGISTER_WRITES)

            # todo: the callback below was commented out because it adds significant delay. git blame me for more info.
            # program_state.inspect.b(
            #     "statement", when=angr.bp_before, action=executed_instruction_hook
            # )
            program_state.inspect.b(
                "mem_read", when=angr.BP_BEFORE, action=memory_read_hook
            )
            program_state.inspect.b(
                "mem_write", when=angr.BP_BEFORE, action=memory_write_hook
            )
            # todo: still necessary ?
            program_state.inspect.remove_breakpoint(
                "constraints", filter_func=lambda x: True
            )
            program_state.inspect.b(
                "exit", when=angr.BP_BEFORE, action=exit_basic_block_hook
            )

            # When we pickle and unpickle a state, the "inspect" callbacks registered to it are lost.
            # We need to attach again the callbacks that were attached for the analysis
            contaminate_tainted_memory_reads_with_taint(program_state)
            do_not_add_constraints_for_tainted_branches(program_state)

            # Remobe the BP `detect_memory_writes_to_tainted_address` in case of generating results from explored_blocks
            # directly returned by the analysis, not from the loaded pickle.
            program_state.inspect.remove_breakpoint(
                "mem_write",
                filter_func=lambda x: x.action.__name__ == "before_memory_write_hook",
            )

            program_state.step()
        # dupl = []
        # for i in range(len(tainting_states)):
        #     for j in range(len(tainting_states)):
        #         if i != j:
        #             logger.debug(f"identical states : {tainting_states[i] == tainting_states[j]}")
        pbar.update()
    pbar.close()
    collector = ResultsCollector()
    target_binary_file_name: str = _angr_project_from_basic_blocks(
        explored_blocks
    ).filename  # type: ignore
    analysis_results = collector.get_analysis_results(target_binary_file_name)
    # block_step_results = collector.get_statement_results()
    block_step_results = collector.get_identical_step_results()
    block_step_results = list(block_step_results)
    # sr_groups = collector.get_identical_step_results()

    ResultsCollector.delete_instance()
    SourceCodeLocator.delete_instances()
    SourceCodeFilesManager.delete_instance()

    return analysis_results, block_step_results


def _angr_project_from_basic_blocks(
    explored_blocks: dict[tuple[int], BasicBlock],
) -> angr.Project:
    """
    This is a helper function to extract the angr project from the list of basic blocks.
    """

    basic_block = next(iter(explored_blocks.values()))

    match basic_block:
        case MultiStatesBasicBlock(states=states):
            p = states[0].project
        case ConsolidatedBasicBlock(state=state):
            p = state.project
        case _:
            raise ValueError

    if p is not None:
        return p
    else:
        raise ValueError("Project is None.")


def executed_instruction_hook(program_state: angr.SimState) -> None:
    # The result of `find_location_in_source_code` may be None
    # It seems that this happens when we make a request for an assembly code point that does not correspond to the
    # code of any source code function.
    src_f: str = program_state.project.filename  # type: ignore
    # logger.debug(src_f)
    locator = SourceCodeLocator(src_f, src_f)
    function_name, file_name, src_l = locator.find_location_in_source_code(
        pc_offset(program_state)
    )
    # logger.debug(f"{function_name}, {file_name}, {src_l}, {src_f}")
    if file_name is not None and src_l is not None:
        collector = ResultsCollector()
        last_b_res = collector.get_last_statement_result()
        if last_b_res is not None:
            previous_source_code_line = last_b_res.src_lnb
        else:
            previous_source_code_line = 0
        if src_l != previous_source_code_line:
            source_file_path = pathlib.Path(file_name)
            src_vars_taint = get_source_code_variables_tainting(program_state)
            src_lines = SourceCodeFilesManager().get_file_lines(
                source_file_path, src_l, src_l
            )

            block_s_res = StatementResult(
                src_file=file_name,
                src_lnb=src_l,
                src_lines=tuple(src_lines),
                src_vars=tuple(src_vars_taint),
            )
            ResultsCollector().add_statement_result(block_s_res)

    else:
        logger.debug(f"{pc_offset(program_state):x}, {src_f}")
        logger.debug("Location in source code not found.")


def memory_read_hook(program_state: angr.SimState) -> None:
    memory_address = program_state.inspect.mem_read_address  # type: ignore
    ResultsCollector().add_analysis_event(
        event_type=EventType.Memory,
        status=status_from_expression(memory_address, program_state),
        instruction_pointer=pc_offset(program_state),
    )


def memory_write_hook(program_state: angr.SimState) -> None:
    memory_address = program_state.inspect.mem_write_address  # type: ignore
    ResultsCollector().add_analysis_event(
        event_type=EventType.Memory,
        status=status_from_expression(memory_address, program_state),
        instruction_pointer=pc_offset(program_state),
    )


def exit_basic_block_hook(program_state: angr.SimState):
    branching_condition = program_state.inspect.exit_guard # type: ignore
    ResultsCollector().add_analysis_event(
        event_type=EventType.Branching,
        status=status_from_expression(branching_condition, program_state),
        instruction_pointer=pc_offset(program_state),
    )


def get_source_code_variables(program_state: angr.SimState) -> dict:
    source_code_variable_names = set(program_state.project.kb.dvars._dvar_containers)  # type: ignore
    source_code_variable_names -= {"argc", "argv"}
    source_code_variable_names = set(
        filter(lambda x: x is not None, source_code_variable_names)
    )
    source_code_variables = {
        name: program_state.dvars[name]  # type: ignore
        for name in source_code_variable_names
        if program_state.dvars[name] is not None  # type: ignore
    }
    source_code_variables_items = filter(
        lambda x: x[1].addr is not None, source_code_variables.items()
    )
    source_code_variables = dict(
        sorted(
            source_code_variables_items,
            key=lambda x: x[1].addr
            if isinstance(x[1].addr, int)
            else x[1].addr.concrete_value,
        )
    )
    return source_code_variables


def get_source_code_variables_tainting(
    program_state: angr.SimState,
) -> list[tuple[str, str]]:
    # as the present function can be called several times at different execution points of the same basic block,
    # we must disable usage of cache. Otherwise, changes in the tainting state while the block is being executed
    # would be lost.
    memory_tainting_state = tainting_state_in_area(
        program_state.memory, use_cache=False
    )

    source_code_variables = get_source_code_variables(program_state)
    out = []
    for variable_i in range(len(source_code_variables)):
        variable_name = list(source_code_variables.keys())[variable_i]
        addr = source_code_variables[variable_name].addr
        variable_address = addr if isinstance(addr, int) else addr.concrete_value

        # todo : Find actual variable size. The commit introducing this line removes a previous tentative of doing this.
        variable_length = 1

        for byte_offset in range(variable_length):
            memory_address = variable_address + byte_offset
            byte_status = memory_tainting_state.get(memory_address)
            if byte_status is None:
                byte_status = "unititialized"
            else:
                byte_status = memory_tainting_state[memory_address]
            out.append((f"{variable_name}+{byte_offset}", byte_status))
    return out
