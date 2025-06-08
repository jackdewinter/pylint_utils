"""
Module to provide a plugin for the project_summarized to deal with
pylint suppressions.
"""

import argparse
import json
import os
from typing import Dict, List, Optional, Tuple, Union

from project_summarizer.plugin_manager.bad_plugin_error import BadPluginError
from project_summarizer.plugin_manager.plugin_details import PluginDetails
from project_summarizer.plugin_manager.project_summarizer_plugin import (
    ProjectSummarizerPlugin,
)
from project_summarizer.summarize_context import SummarizeContext


class PylintSuppressionSummarizerPlugin(ProjectSummarizerPlugin):
    """
    Class to provide a plugin for the project_summarized to deal with
    pylint suppressions.
    """

    __COMMAND_LINE_ARGUMENT = "--pylint-suppressions"
    __COMMAND_LINE_OPTION = "suppressions_file"

    __PLUGIN_ID = "PYLINT-SUPPRESSIONS"
    __PLUGIN_NAME = "PyLint Suppressions Summary"
    __PLUGIN_VERSION = "0.5.0"

    def __init__(self) -> None:
        super().__init__()
        self.__output_path: str = ""
        self.__context: Optional[SummarizeContext] = None

    def get_details(self) -> PluginDetails:
        return PluginDetails(
            PylintSuppressionSummarizerPlugin.__PLUGIN_ID,
            PylintSuppressionSummarizerPlugin.__PLUGIN_NAME,
            PylintSuppressionSummarizerPlugin.__PLUGIN_VERSION,
            ProjectSummarizerPlugin.VERSION_BASIC,
        )

    def set_context(self, context: SummarizeContext) -> None:
        """
        Set the context for the plugins.
        """
        self.__context = context
        self.__output_path = os.path.join(
            self.__context.report_dir, "pylint_suppression.json"
        )

    def get_output_path(self) -> str:
        """
        Get the output path for the reporting file.
        """
        return self.__output_path

    def add_command_line_arguments(
        self, parser: argparse.ArgumentParser
    ) -> Tuple[str, str]:
        """
        Add a command line argument to denote the file to scan.
        """

        parser.add_argument(
            PylintSuppressionSummarizerPlugin.__COMMAND_LINE_ARGUMENT,
            dest=PylintSuppressionSummarizerPlugin.__COMMAND_LINE_OPTION,
            metavar="path",
            action="store",
            default="",
            help="Source file name for cobertura test coverage reporting.",
        )
        return (
            PylintSuppressionSummarizerPlugin.__COMMAND_LINE_ARGUMENT,
            PylintSuppressionSummarizerPlugin.__COMMAND_LINE_OPTION,
        )

    @classmethod
    def __load_previous_summary_file(cls, test_results_to_load: str) -> Dict[str, int]:
        """
        Attempt to load a previously published test summary.
        """

        previous_totals: Dict[str, int] = {}
        previous_file_path = os.path.abspath(test_results_to_load)
        if os.path.exists(previous_file_path) and os.path.isfile(previous_file_path):
            try:
                with open(
                    previous_file_path,
                    "r",
                    encoding=ProjectSummarizerPlugin.DEFAULT_FILE_ENCODING,
                ) as infile:
                    results_dictionary = json.load(infile)
            except json.decoder.JSONDecodeError as this_exception:
                raise BadPluginError(
                    formatted_message=f"Previous coverage summary file '{test_results_to_load}' "
                    + f"is not a valid JSON file ({this_exception})."
                ) from this_exception
            except IOError as this_exception:
                raise BadPluginError(
                    formatted_message=f"Previous coverage summary file '{test_results_to_load}' "
                    + f"was not loaded ({this_exception})."
                ) from this_exception
            previous_totals = results_dictionary["disables-by-name"]
        return previous_totals

    def generate_report(
        self, only_changes: bool, column_width: int, report_file: str
    ) -> Optional[Tuple[List[str], List[str], List[List[str]]]]:
        """
        Generate the report and display it.
        """
        try:
            with open(report_file, encoding="utf-8") as suppression_file:
                suppression_data = json.load(suppression_file)
        except OSError as this_exception:
            raise BadPluginError(
                formatted_message="File error opening report file: "
                + str(this_exception)
            ) from this_exception
        except json.JSONDecodeError as this_exception:
            raise BadPluginError(
                formatted_message="File error reading report file as a json file: "
                + str(this_exception)
            ) from this_exception

        if (
            "disables-by-file" not in suppression_data
            or "disables-by-name" not in suppression_data
        ):
            raise BadPluginError(
                formatted_message="Report file does not appear to be a pylint_utils generated file."
            )

        new_stats = {"disables-by-name": suppression_data["disables-by-name"]}
        self.save_summary_file(self.__output_path, new_stats, "PyLint Suppressions")

        report_rows = None
        if column_width:
            assert self.__context is not None
            published_summary_path = self.__context.compute_published_path_to_file(
                self.__output_path
            )
            loaded_stats = self.__load_previous_summary_file(published_summary_path)
            report_rows = self.__calculate_row_differences(
                new_stats["disables-by-name"], loaded_stats, only_changes
            )
        return report_rows

    @classmethod
    def __format_coverage_value(
        cls, new_row: List[str], value: str, delta: str
    ) -> None:
        """
        Helper method to consistently format the coverage value/delta.
        """
        new_row.append(value)
        delta_value = delta
        if delta_value != "0" and not delta_value.startswith("-"):
            delta_value = f"+{delta_value}"
        new_row.append(delta_value)

    def __calculate_row_differences(
        self,
        new_stats: Dict[str, int],
        loaded_stats: Dict[str, int],
        only_changes: bool,
    ) -> Optional[Tuple[List[str], List[str], List[List[str]]]]:

        new_keysx = set(new_stats.keys())
        new_keys = sorted(list(new_keysx.union(loaded_stats.keys())))

        display_rows = []
        for next_key in new_keys:
            line_data: List[Union[str, int]] = []
            if next_key in new_stats:
                if next_key in loaded_stats:
                    line_data = [
                        next_key,
                        new_stats[next_key],
                        new_stats[next_key] - loaded_stats[next_key],
                    ]
                else:
                    line_data = [next_key, new_stats[next_key], new_stats[next_key]]
            else:
                assert next_key in loaded_stats
                line_data = [next_key, 0, -loaded_stats[next_key]]
            if line_data and (not only_changes or line_data[2]):
                new_row = [next_key]
                self.__format_coverage_value(
                    new_row, str(line_data[1]), str(line_data[2])
                )
                display_rows.append(new_row)

        print("PyLint Suppression Summary\n---------------------\n")
        if not display_rows:
            print(
                "PyLint suppressions have not changed since last published suppressions."
            )
            print()
            return None
        hdrs = ["Suppression", "Count", "Delta"]
        justify_columns = ["l", "r", "r"]
        return (hdrs, justify_columns, display_rows)
