import os
import logging
import datetime
import math
import pickle
import shutil
import json
from dataclasses import asdict
from argparse import ArgumentParser
from glob import glob
from pathlib import Path
from marshmallow import ValidationError

import yaml

try:
    from git import Repo
except Exception:
    pass

from ya_cttool import TargetConfigManager, do_analysis, log
from ya_cttool.core.models import StatementResultSchema
from ya_cttool.log import enable_file_logging, set_log_file

from .evaluation import (
    EvalSummary,
    EvalSummarySchema,
    evaluate,
    TestingResultItem,
    TestingResultItemSchema,
)
from .config import ConfigManager as TestConfigManager
from .compilation import compile

logger = logging.getLogger(log.LOGGER_NAME)


def load_results(path: str) -> list[TestingResultItem]:
    with open(path) as f:
        content_dict = json.load(f)
    # s = ResultItemSchema(many=True)
    out = TestingResultItemSchema.load(content_dict["results"], many=True)
    return out  # type: ignore


def count_folders(path) -> int:
    return sum(os.path.isdir(os.path.join(path, entry)) for entry in os.listdir(path))


def run(args):
    global logger
    test_config_path = args.config

    conf_manager = TestConfigManager().load_configs(test_config_path)

    TargetConfigManager(config=conf_manager.target_config)

    now = datetime.datetime.now().timestamp()
    results_foler = f"run_{math.trunc(now)}"
    results_path = os.path.join(conf_manager.test_config.results_dir, results_foler)
    if conf_manager.test_config.test_mode:
        results_path = f"{results_path}-test"
    os.mkdir(results_path)

    enable_file_logging(
        filename=os.path.join(results_path, "logs.json"), level=logging.INFO
    )
    logger = logging.getLogger(log.LOGGER_NAME)

    logger.info("Test begins.")

    try:
        repo = Repo(".")  # type: ignore
        current_branch = repo.active_branch.name
        last_commit = repo.head.commit.hexsha
        logger.info(f"Current branch {current_branch}")
        logger.info(f"Last commit {last_commit}")
    except Exception:
        current_branch = ""
        last_commit = ""

    TestConfigManager().dump(results_path)
    compiler_info_path = os.path.join(
        conf_manager.test_config.cases_bin_dir,
        conf_manager.test_config.compiler_info_file,
    )
    shutil.copy(
        compiler_info_path,
        os.path.join(results_path, conf_manager.test_config.compiler_info_file),
    )

    for bin in conf_manager.test_config.cases_bin:
        res_path = os.path.join(results_path, bin)
        os.mkdir(res_path)
        if not os.path.isdir(res_path):
            logger.error(f"Error : {res_path} does not exists")
            exit(f"Error : {res_path} does not exists")
        set_log_file(os.path.join(res_path, "logs.json"), logging.INFO)
        bin_path = os.path.join(conf_manager.test_config.cases_bin_dir, bin)

        expected = load_results(
            os.path.join(conf_manager.test_config.cases_expected_dir, f"{bin}.json")
        )

        (
            res_metadata,
            analysis_metadata,
            explored_states,
            results,
            block_step_results,
        ) = do_analysis(bin_path)
        metadata = res_metadata | analysis_metadata
        
        # Quick fix because of model change in the project core
        _results = [
            TestingResultItem(
                source_file=it.source.file,
                line=it.source.line,
                type=it.type,
                color=it.color,
            )
            for it in results
            if it.source is not None
        ]

        comp_res, metrics = evaluate(_results, expected)
        _, metrics_expected = evaluate(expected, expected)

        if metrics == metrics_expected:
            test_passed = True
        else:
            test_passed = False
            logger.error(
                f"Expected results do not correpond to actual results for {bin}"
            )
            if conf_manager.test_config.fail:
                exit(1)

        metadata["bin_name"] = bin
        metadata["git"] = {"branch": current_branch, "commit": last_commit}
        shutil.copy(bin_path, os.path.join(res_path, bin))

        result_summary = EvalSummary(test_passed, metrics)

        with open(os.path.join(res_path, "metadata.yml"), "w") as f:
            yaml.dump(metadata, f)
        with open(os.path.join(res_path, "result_summary.json"), "w") as f:
            res_summ_s = EvalSummarySchema()
            f.write(res_summ_s.dumps(result_summary, indent=4))
        with open(os.path.join(res_path, "block_step_results.json"), "w") as f:
            # sch = StatementResultSchema(many=True)
            json_s = StatementResultSchema.dumps(block_step_results, indent=4)
            f.write(json_s)
        with open(os.path.join(res_path, "comparison_results.json"), "w") as f:
            json.dump(asdict(comp_res), f, indent=4)
        if conf_manager.test_config.save_explored_states:
            with open(os.path.join(res_path, "explored_states.pkl"), "wb") as f:
                pickle.dump(explored_states, f, -1)


def check_results(args):
    config_manager = TestConfigManager().load_configs(args.config)
    res_path = config_manager.test_config.results_dir

    res_folders = glob(f"{res_path}/run_*")
    res_folders.sort()

    if len(res_folders) > 1:
        last = res_folders[-1]
    elif len(res_folders) == 1:
        last = res_folders[0]
    else:
        raise Exception("No result available.")

    res_summaries = glob(f"{last}/**/result_summary.json")

    logger.info(f"Found {len(res_summaries)} result's summaries")

    if len(res_summaries) == 0:
        raise Exception(f"{res_path} : missing result_summary.json files")

    tests_passed = []
    res_summ_s = EvalSummarySchema()

    for res in res_summaries:
        with open(res) as f:
            res_dict = json.load(f)

        try:
            res_obj: EvalSummary = res_summ_s.load(res_dict)  # type: ignore
        except ValidationError as e:
            logger.error(e)
            continue

        if not res_obj.test_passed:
            logger.error(f"Test failed for {res}")
        tests_passed.append(res_obj.test_passed)

    assert all(tests_passed), "Some tests did not pass."
    msg = f"{last} : {len(tests_passed)} tests passed as the folder may contain {count_folders(last)} tests."
    logger.info(msg)
    print(msg)
    assert len(tests_passed) == count_folders(last) and count_folders(last), (
        "Some folders do not contain a valid result_summary.json file."
    )


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--config", required=True, type=Path, help="The test configuration to use."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("run", help="Run the tests.").set_defaults(func=run)
    subparsers.add_parser(
        "check_results", help="Checks the results of the last test run."
    ).set_defaults(func=check_results)
    subparsers.add_parser("compile", help="Compile the tests.").set_defaults(
        func=compile
    )
    args = parser.parse_args()
    args.func(args)
