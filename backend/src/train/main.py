#!/usr/bin/env python3
"""Run one or more pipeline stages with shared settings."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from pathlib import Path

if __package__ in (None, ""):
    src_dir = Path(__file__).resolve().parents[1]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

import train.stages.evaluate_model as evaluate_model
import train.stages.prepare_data as prepare_data
import train.stages.run_eda as run_eda
import train.stages.train_model as train_model
from train.settings import get_scripts_settings

StageCallable = Callable[[], None]


def run_stage(name: str) -> None:
    stage_map: dict[str, StageCallable] = {
        "prepare": prepare_data.main,
        "train": train_model.main,
        "evaluate": evaluate_model.main,
        "eda": run_eda.main,
    }
    if name not in stage_map:
        raise ValueError(f"Unknown stage '{name}'")
    stage_map[name]()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ML pipeline stages.")
    parser.add_argument(
        "--stages",
        nargs="+",
        default=["prepare", "train", "evaluate"],
        choices=["prepare", "train", "evaluate", "eda", "all"],
        help="Stages to run in order. Use 'all' for full pipeline.",
    )
    args = parser.parse_args()

    settings = get_scripts_settings()
    selected = args.stages
    if "all" in selected:
        selected = ["prepare", "train", "evaluate", "eda"]

    print(f"Using source data: {settings.source_data_path}")
    print(f"Using model dir:   {settings.predictor_dir}")
    print(f"Using report path: {settings.evaluation_report_path}")
    for stage_name in selected:
        print(f"Running stage: {stage_name}")
        run_stage(stage_name)


if __name__ == "__main__":
    main()
