import logging
import os
import json
from pathlib import Path
import pickle
import sys
from typing_extensions import Annotated, NoReturn

from marshmallow.exceptions import ValidationError
import typer


from .core.models import StatementResultSchema, ResultItemSchema
from .analysis import run_analysis_with_consolidation_threshold, do_analysis
from .config import CommonConfig, TargetConfigManager
from .exception import AnalysisInterruptError, AnalysisInterruptKind
from .log import LOGGER_NAME, configure_logger_from_config
from .result import compute_results


logger = logging.getLogger(LOGGER_NAME)

app = typer.Typer()

_config_help = "Path to the configuration file specific to the target."
_target_help = "Path to the target to analyze."

def printe(content):
    typer.echo(content, file=sys.stderr)


def exit_failure(msg: str = "ERROR : Unexpected failure.") -> NoReturn:
    printe(msg)
    raise typer.Exit(code=1)

@app.command()
def analyze(
    config: Annotated[str, typer.Option(help=_config_help)],
    target: Annotated[str, typer.Option(help=_target_help)],
):
    """Run the analysis phase only on the target."""
    cmn_cfg, tgt_cfg, res_p = setup(target, config, make_dir=True)

    metadata, explored_states = run_analysis_with_consolidation_threshold(
        target, tgt_cfg.get_config().max_consolidation_threshold
    )

    if cmn_cfg.outputs.save_metadata:
        with open(os.path.join(res_p, "analysis_metadata.json"), "w") as f:
            json.dump(metadata, f)

    _save_explored_states(explored_states, res_p)


@app.command()
def results(
    config: Annotated[str, typer.Option(help=_config_help)],
    target: Annotated[str, typer.Option(help=_target_help)],
):
    """Run the results computation phase only on the target."""
    cmn_cfg, _, res_p = setup(target, config, make_dir=False)

    if not res_p.exists():
        msg = f"No results available for {target}."
        logger.error(msg)
        printe(msg)
        exit(1)

    with open(os.path.join(res_p, "explored_states.pkl"), "rb") as f:
        explored_states = pickle.load(f)

    metadata, res_items, block_step_results = compute_results(explored_states)

    if cmn_cfg.outputs.save_results:
        with open(os.path.join(res_p, "block_results.json"), "w") as f:
            json_s = StatementResultSchema.dumps(block_step_results, indent=4,many=True)
            f.write(json_s)
        with open(os.path.join(res_p, "leaks_results.json"), "w") as f:
            json_s = ResultItemSchema.dumps(res_items, indent=4,many=True)
            f.write(json_s)
    else:
        for bsr in block_step_results:
            bsr.display()
        for item in res_items:
            if item.source is not None:
                typer.echo(
                    f"Leak detected : {item.source.file}:{item.source.line} [{item.type.name}:{item.color.name}]"
                )

    if cmn_cfg.outputs.save_metadata:
        with open(os.path.join(res_p, "results_metadata.json"), "w") as f:
            json.dump(metadata, f)


@app.command()
def full(
    config: Annotated[str, typer.Option(help=_config_help)],
    target: Annotated[str, typer.Option(help=_target_help)],
):
    """Run both analysis and results computation phases."""

    cmn_cfg, _, res_p = setup(target, config, make_dir=True)
    try:
        res_metadata, analysis_metadata, explored_states, results, block_step_results = (
            do_analysis(target)
        )
        analysis_metadata['end'] = AnalysisInterruptKind.NoInterrupt.name 
    except AnalysisInterruptError as exc:
        match exc.kind:
            case AnalysisInterruptKind.KeyboardInterrupt:
                exit_failure("Aborted.")
            case _:
                explored_states = exc.discovered_blocks
                res_metadata, results, block_step_results = compute_results(
                    explored_states
                )
                analysis_metadata = {
                    "end": exc.kind.name
                }
                printe("WARNING: Managed interrupt : partial results only !!!")
    except Exception as e:
        logger.error("An unexpected error occured.")
        logger.error(type(e))
        logger.debug(e)
        exit_failure()
        
    if cmn_cfg.outputs.save_metadata:
        metadata = res_metadata | analysis_metadata
        if metadata.get("angr_state_options") is not None:
            del metadata["angr_state_options"]
        with open(os.path.join(res_p, "metadata.json"), "w") as f:
            json.dump(metadata, f)
    if cmn_cfg.outputs.save_explored_states:
        _save_explored_states(explored_states, res_p)

    _save_or_print_results(cmn_cfg, res_p, block_step_results, results)


def setup(
    target: str, target_config_file: str, make_dir=False
) -> tuple[CommonConfig, TargetConfigManager, Path]:
    try:
        cmn_c = CommonConfig()
        TargetConfigManager(path=target_config_file)
    except ValidationError as exc:
        logger.error(exc)
        printe("The target configuration file is not valid.",)
        exit(1)

    target_p = Path(target)
    if not target_p.exists():
        logger.error(f"{target} does not exists.")
        printe(f"{target} does not exists.")
        exit(1)

    res_p = Path(os.path.join(cmn_c.outputs.dir, target_p.name))
    if make_dir:
        os.makedirs(res_p, exist_ok=True)

    configure_logger_from_config(cmn_c.logging, os.path.join(res_p, "logs.json"))

    return cmn_c, TargetConfigManager(), res_p


def _save_explored_states(explored_states, dest):
    printe("Saving explored states...")
    out_path = os.path.join(dest, "explored_states.pkl")
    with open(out_path, "wb") as f:
        # -1 as last argument is needed, according to the angr documentation
        # https://docs.angr.io/en/latest/faq.html#how-do-i-serialize-angr-objects
        pickle.dump(explored_states, f, -1)


def _save_or_print_results(config, res_p, block_step_results, res_items):
    if config.outputs.save_results:
        with open(os.path.join(res_p, "block_results.json"), "w") as f:
            json_s = StatementResultSchema.dumps(block_step_results, indent=4,many=True)
            f.write(json_s)
            typer.echo(f"File saved : {f.name}")

        with open(os.path.join(res_p, "leaks_results.json"), "w") as f:
            json_s = ResultItemSchema.dumps(res_items, indent=4, many=True)
            f.write(json_s)
            typer.echo(f"File saved : {f.name}")
    else:
        for bsr in block_step_results:
            bsr.display()
        for item in res_items:
            typer.echo(
                f"Leak detected : {item.source.file}:{item.source.line} [{item.type.name}:{item.color.name}]"
            )
