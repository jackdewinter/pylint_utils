"""
Module to provide a scanner for PyLint suppression comments.
"""

import json
import sys


class PyLintCommentScanner:
    """
    Class to provide a scanner for PyLint suppression comments.
    """

    __pylint_suppression_prefix = "# pylint:"
    __pylint_suppression_disable = "disable="
    __pylint_suppression_disable_next = "disable-next="
    __pylint_suppression_enable = "enable="
    __too_many_lines_item = "too-many-lines"

    def __init__(self):
        self.__scan_map = {}
        self.__current_file_name = None
        self.__errors_reported = None
        self.__disabled_by_file_name_map = None

    @property
    def scan_map(self):
        """
        Scan map of each enabled and disabled pylint rule.
        """
        return self.__scan_map

    def analyze_python_files_for_pylint_comments(self, args, files_to_scan):
        """
        Analyze the specifed python files, looking for mismatched PyLint comments lines.
        """

        self.__disabled_by_file_name_map = {}
        total_error_count = 0
        for next_file in files_to_scan:

            if args.verbose_mode:
                print(f"Scanning file: {next_file}")

            with open(next_file, encoding="utf-8") as python_file:
                python_file_content = python_file.readlines()
            (
                disable_count_map,
                error_count,
                disable_enabled_log,
            ) = self.__check_contents_of_python_file(next_file, python_file_content)
            total_error_count += error_count
            self.__disabled_by_file_name_map[next_file] = disable_count_map

            if not error_count:
                self.__scan_map[next_file] = (disable_enabled_log, python_file_content)
            if args.verbose_mode:
                print(f"  File contains {error_count} scan errors.")

        return total_error_count

    def __check_contents_of_python_file(self, file_name, file_contents):

        self.__current_file_name = file_name
        self.__errors_reported = 0

        active_items_map = {}
        line_count = 1
        total_disable_counts = {}
        disable_enabled_log = []
        for next_line in file_contents:
            stripped_next_line = next_line.strip()
            if stripped_next_line.startswith(
                PyLintCommentScanner.__pylint_suppression_prefix
            ):
                pylint_directive = stripped_next_line[
                    len(PyLintCommentScanner.__pylint_suppression_prefix) :
                ].strip()
                if pylint_directive.startswith(
                    PyLintCommentScanner.__pylint_suppression_disable
                ):
                    collected_items = self.__decompose_valid_pylint_line(
                        pylint_directive,
                        PyLintCommentScanner.__pylint_suppression_disable,
                    )
                    self.__record_disabled_items(
                        active_items_map,
                        line_count,
                        total_disable_counts,
                        collected_items,
                    )
                elif pylint_directive.startswith(
                    PyLintCommentScanner.__pylint_suppression_enable
                ):
                    collected_items = self.__decompose_valid_pylint_line(
                        pylint_directive,
                        PyLintCommentScanner.__pylint_suppression_enable,
                    )
                    self.__record_enabled_items(
                        active_items_map,
                        line_count,
                        collected_items,
                        disable_enabled_log,
                    )
                elif pylint_directive.startswith(
                    PyLintCommentScanner.__pylint_suppression_disable_next
                ):
                    self.__report_warning(
                        line_count,
                        "Pylint suppression string "
                        + f"'{PyLintCommentScanner.__pylint_suppression_disable_next}' is not supported.",
                    )
                else:
                    self.__report_error(
                        line_count,
                        f"Pylint suppression '{pylint_directive}' is not understood.",
                    )
            line_count += 1
        if active_items_map:
            for lowercase_next_item in active_items_map:
                self.__report_error(
                    line_count,
                    f"Pylint error '{lowercase_next_item}' was disabled, but not re-enabled.",
                )

        return total_disable_counts, self.__errors_reported, disable_enabled_log

    @classmethod
    def __decompose_valid_pylint_line(cls, directive_text, directive_action):
        remaining_line = directive_text[len(directive_action) :]

        collected_items = []
        next_comma_index = remaining_line.find(",")
        while next_comma_index != -1:
            part_before_comma = remaining_line[:next_comma_index].strip()
            collected_items.append(part_before_comma)
            remaining_line = remaining_line[next_comma_index + 1 :].strip()
            next_comma_index = remaining_line.find(",")
        collected_items.append(remaining_line.strip())

        return collected_items

    def __report_error(self, line_count, error_string):
        print(f"{self.__current_file_name}({line_count}): {error_string}")
        self.__errors_reported += 1

    def __report_warning(self, line_count, warning_string):
        print(f"{self.__current_file_name}({line_count}): {warning_string}")

    def __record_disabled_items(
        self, active_items_map, line_count, total_disable_counts, list_of_items
    ):
        for next_item in list_of_items:
            lowercase_next_item = next_item.lower()
            if lowercase_next_item == PyLintCommentScanner.__too_many_lines_item:
                continue
            if lowercase_next_item in active_items_map:
                self.__report_error(
                    line_count,
                    f"Pylint error '{lowercase_next_item}' was already disabled.",
                )
            else:
                active_items_map[lowercase_next_item] = line_count

            if next_item in total_disable_counts:
                current_count = total_disable_counts[next_item]
            else:
                current_count = 0
            current_count += 1
            total_disable_counts[next_item] = current_count

    def __record_enabled_items(
        self, active_items_map, line_count, list_of_items, disable_enabled_log
    ):
        for next_item in list_of_items:
            lowercase_next_item = next_item.lower()
            if lowercase_next_item == PyLintCommentScanner.__too_many_lines_item:
                continue
            if lowercase_next_item not in active_items_map:
                self.__report_error(
                    line_count,
                    f"Pylint error '{lowercase_next_item}' was not disabled, so enable is ignored.",
                )
            else:
                line_disabled_on = active_items_map[lowercase_next_item]
                del active_items_map[lowercase_next_item]
                new_entry = (line_disabled_on, line_count, next_item)
                disable_enabled_log.append(new_entry)

    @classmethod
    def __create_report_map(cls, disabled_by_file_name_map):
        total_counts = {}
        for file_name, next_file_map in disabled_by_file_name_map.items():
            next_file_map = disabled_by_file_name_map[file_name]

            for disable_item in next_file_map:
                added_count = next_file_map[disable_item]

                new_count = (
                    total_counts[disable_item] + added_count
                    if disable_item in total_counts
                    else added_count
                )
                total_counts[disable_item] = new_count

        return {
            "disables-by-file": disabled_by_file_name_map,
            "disables-by-name": total_counts,
        }

    def create_report(self, args):
        """
        Given that the `analyze_python_files_for_pylint_comments` function was already
        executed, generate a json report of what was found.
        """

        return_code = 0
        entire_map = self.__create_report_map(self.__disabled_by_file_name_map)

        try:
            with open(args.report_file, "wt", encoding="utf-8") as outfile:
                json.dump(entire_map, outfile, indent=4)
        except IOError as this_exception:
            clean_this_exception = str(this_exception).replace("\\\\", "\\")
            print(
                f"Unable to write to report file '{args.report_file}':\n"
                + f"  Error: {clean_this_exception}",
                file=sys.stderr,
            )
            return_code = 1
        return return_code
