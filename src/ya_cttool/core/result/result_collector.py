
import functools
from collections import defaultdict
from typing_extensions import Self

from ..models import AnalysisEvent, StatementResult, ResultItem, Color, EventType, Source
from ..tainting import get_over_approximation_of_statuses
from ...common import SourceCodeLocator


class ResultsCollector:
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super(ResultsCollector, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._statement_results = []
        self._analysis_events: set[AnalysisEvent] = set()
        self._initialized = True

    def get_identical_step_results(self) -> dict:
        groups = defaultdict(list)
        for sr in self._statement_results:
            groups[sr].append(sr)
        return groups

    def add_statement_result(self, bsr: StatementResult):
        # bsr.display()
        self._statement_results.append(bsr)

    def get_analysis_results(self, target_binary_filename: str) -> list[ResultItem]:
        """
        Computes the CT violations discovered during the analysis.

        A CT violation has type red if the problematic memory address or branching condition is red in all tainting states
        associated to the program point. Otherwise, it has type orange.
        """

        def result_item_from_analysis_event(analysis_event: AnalysisEvent):
            locator = SourceCodeLocator(target_binary_filename, target_binary_filename)
            address = analysis_event.program_point
            funcname, file_name, source_code_line = locator.find_location_in_source_code(
                address
            )

            assert file_name is not None and source_code_line is not None and funcname is not None

            match analysis_event.status:
                case "red":
                    color = Color.Red
                case "orange":
                    color = Color.Orange
                case _:
                    assert False

            return ResultItem(
                binary_file=target_binary_filename,
                binary_address=address,
                type=analysis_event.type,
                color=color,
                source=Source(
                    file=file_name,
                    line=source_code_line,
                    fullpath="",
                    funcname=funcname
                )
            )

        return [
            result_item_from_analysis_event(analysis_event)
            for analysis_event in self.get_consolidated_analysis_events()
            if analysis_event.status in ["red", "orange"]
        ]

    def get_consolidated_analysis_events(self) -> list[AnalysisEvent]:
        """
        Returns the list of analysis events after consolidation.

        This function groups the analysis events by program points and types (memory access or branching) and consolidates each
        group into a single analysis event, whose status is the over approximation of the statuses of the events in the group.
        """

        def consolidate_analysis_events(event_type: EventType, program_point: int):
            filtered_analysis_events = [
                event
                for event in self._analysis_events
                if event.type == event_type and event.program_point == program_point
            ]

            consolidated_status = functools.reduce(
                get_over_approximation_of_statuses,
                (event.status for event in filtered_analysis_events),
            )

            return AnalysisEvent(
                program_point=program_point, type=event_type, status=consolidated_status
            )

        memory_event_program_points = set(
            event.program_point
            for event in self._analysis_events
            if event.type == EventType.Memory
        )

        consolidated_memory_events = [
            consolidate_analysis_events(EventType.Memory, program_point)
            for program_point in memory_event_program_points
        ]

        branching_event_program_points = set(
            event.program_point
            for event in self._analysis_events
            if event.type == EventType.Branching
        )

        consolidated_branching_events = [
            consolidate_analysis_events(EventType.Branching, program_point)
            for program_point in branching_event_program_points
        ]

        return consolidated_memory_events + consolidated_branching_events

    def get_statement_results(self):
        return self._statement_results

    def get_last_statement_result(self) -> StatementResult | None:
        if len(self._statement_results) > 0:
            return self._statement_results[-1]
        else:
            return None

    def add_analysis_event(
        self, event_type: EventType, status: Color | int, instruction_pointer: int
    ):
        self._analysis_events.add(
            AnalysisEvent(
                program_point=instruction_pointer, type=event_type, status=status
            )
        )

    @classmethod
    def delete_instance(cls):
        cls._instance = None

