"""
Module to ...
"""

import argparse
import glob
import json
import logging
import os
import os.path as osp
import runpy
import subprocess
import sys
import time

LOGGER = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class PyLintUtils:
    """
    Class to provide for...
    """

    __available_log_maps = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    __pylint_suppression_prefix = "# pylint:"
    __pylint_suppression_disable = "disable="
    __pylint_suppression_enable = "enable="
    __too_many_lines_item = "too-many-lines"
    __default_log_level = "CRITICAL"

    def __init__(self):
        (
            self.__version_number,
            self.default_log_level,
        ) = (PyLintUtils.__get_semantic_version(), PyLintUtils.__default_log_level)
        self.__current_file_name = None
        self.errors_reported = None
        self.__scan_map = {}
        self.__verbose_mode = None
        self.__is_being_piped = None
        self.__new_handler = None

    @staticmethod
    def __get_semantic_version():
        file_path = __file__
        assert os.path.isabs(file_path)
        file_path = file_path.replace(os.sep, "/")
        last_index = file_path.rindex("/")
        file_path = file_path[0 : last_index + 1] + "version.py"
        version_meta = runpy.run_path(file_path)
        return version_meta["__version__"]

    @staticmethod
    def __log_level_type(argument):
        """
        Function to help argparse limit the valid log levels.
        """
        if argument in PyLintUtils.__available_log_maps:
            return argument
        raise ValueError("Value '" + argument + "' is not a valid log level.")

    def __parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Analyze any found Python files for PyLint suppressions."
        )
        parser.add_argument(
            "--version", action="version", version=f"{self.__version_number}"
        )

        parser.add_argument(
            "--log-level",
            dest="log_level",
            action="store",
            default=PyLintUtils.__default_log_level,
            help="minimum level for any log messages",
            type=PyLintUtils.__log_level_type,
            choices=list(PyLintUtils.__available_log_maps.keys()),
        )
        parser.add_argument(
            "--log-file",
            dest="log_file",
            action="store",
            help="destination file for log messages",
        )
        parser.add_argument(
            "--config",
            dest="config_file",
            action="store",
            help="PyLint configuration file (for verify only)",
        )
        parser.add_argument(
            "-s",
            "--scan",
            dest="scan_suppressions",
            action="store_true",
            default=False,
            help="scan for unused PyLint suppressions",
        )
        parser.add_argument(
            "-r",
            "--report",
            dest="report_file",
            action="store",
            help="destination file for disabled errors report",
        )
        parser.add_argument(
            "-l",
            "--list-files",
            dest="list_files",
            action="store_true",
            default=False,
            help="list the markdown files found and exit",
        )
        parser.add_argument(
            "-v",
            "--verbose",
            dest="verbose_mode",
            action="store_true",
            default=False,
            help="show lots of stuff",
        )
        parser.add_argument(
            "paths",
            metavar="path",
            type=str,
            nargs="+",
            help="One or more paths to scan for eligible files",
        )

        return parser.parse_args()

    @classmethod
    def __decompose_valid_pyline_line(cls, directive_text, directive_action):
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
        self.errors_reported += 1

    def __record_disabled_items(
        self, active_items_map, line_count, total_disable_counts, list_of_items
    ):
        for next_item in list_of_items:
            lowercase_next_item = next_item.lower()
            if lowercase_next_item == PyLintUtils.__too_many_lines_item:
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

    def __record_enable_items(
        self, active_items_map, line_count, list_of_items, disable_enabled_log
    ):
        for next_item in list_of_items:
            lowercase_next_item = next_item.lower()
            if lowercase_next_item == PyLintUtils.__too_many_lines_item:
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

    def __check_contents_of_python_file(self, file_name, file_contents):

        self.__current_file_name = file_name
        self.errors_reported = 0

        active_items_map = {}
        line_count = 1
        total_disable_counts = {}
        disable_enabled_log = []
        for next_line in file_contents:
            stripped_next_line = next_line.strip()
            if stripped_next_line.startswith(PyLintUtils.__pylint_suppression_prefix):
                pylint_directive = stripped_next_line[
                    len(PyLintUtils.__pylint_suppression_prefix) :
                ].strip()
                if pylint_directive.startswith(
                    PyLintUtils.__pylint_suppression_disable
                ):
                    collected_items = self.__decompose_valid_pyline_line(
                        pylint_directive, PyLintUtils.__pylint_suppression_disable
                    )
                    self.__record_disabled_items(
                        active_items_map,
                        line_count,
                        total_disable_counts,
                        collected_items,
                    )
                elif pylint_directive.startswith(
                    PyLintUtils.__pylint_suppression_enable
                ):
                    collected_items = self.__decompose_valid_pyline_line(
                        pylint_directive, PyLintUtils.__pylint_suppression_enable
                    )
                    self.__record_enable_items(
                        active_items_map,
                        line_count,
                        collected_items,
                        disable_enabled_log,
                    )
            line_count += 1
        if active_items_map:
            for lowercase_next_item in active_items_map:
                self.__report_error(
                    line_count,
                    f"Pylint error '{lowercase_next_item}' was disabled, but not re-enabled.",
                )

        return total_disable_counts, self.errors_reported, disable_enabled_log

    @classmethod
    def __handle_list_files(cls, files_to_scan):

        if files_to_scan:
            print("\n".join(files_to_scan))
            return 0
        print("No matching files found.", file=sys.stderr)
        return 1

    @classmethod
    def __is_file_eligible_to_scan(cls, path_to_test):
        """
        Determine if the presented path is one that we want to scan.
        """
        return path_to_test.endswith(".py")

    def __process_next_path(self, next_path, files_to_parse):

        did_find_any = False
        LOGGER.info("Determining files to scan for path '%s'.", next_path)
        if not os.path.exists(next_path):
            print(
                f"Provided path '{next_path}' does not exist.",
                file=sys.stderr,
            )
            LOGGER.debug("Provided path '%s' does not exist.", next_path)
        elif os.path.isdir(next_path):
            LOGGER.debug(
                "Provided path '%s' is a directory. Walking directory.", next_path
            )
            did_find_any = True
            for root, _, files in os.walk(next_path):
                root = root.replace("\\", "/")
                for file in files:
                    rooted_file_path = root + "/" + file
                    if self.__is_file_eligible_to_scan(rooted_file_path):
                        files_to_parse.add(rooted_file_path)
        elif self.__is_file_eligible_to_scan(next_path):
            LOGGER.debug(
                "Provided path '%s' is a valid file. Adding.",
                next_path,
            )
            files_to_parse.add(next_path)
            did_find_any = True
        else:
            LOGGER.debug(
                "Provided path '%s' is not a valid file. Skipping.",
                next_path,
            )
            print(
                f"Provided file path '{next_path}' is not a valid file. Skipping.",
                file=sys.stderr,
            )
        return did_find_any

    def __determine_files_to_scan(self, eligible_paths):

        did_error_scanning_files = False
        files_to_parse = set()
        for next_path in eligible_paths:
            if "*" in next_path or "?" in next_path:
                globbed_paths = glob.glob(next_path)
                if not globbed_paths:
                    print(
                        f"Provided glob path '{next_path}' did not match any files.",
                        file=sys.stderr,
                    )
                    did_error_scanning_files = True
                    break
                for next_globbed_path in globbed_paths:
                    next_globbed_path = next_globbed_path.replace("\\", "/")
                    self.__process_next_path(next_globbed_path, files_to_parse)
            elif not self.__process_next_path(next_path, files_to_parse):
                did_error_scanning_files = True
                break

        files_to_parse = list(files_to_parse)
        files_to_parse.sort()

        LOGGER.info("Number of files found: %s", str(len(files_to_parse)))
        return files_to_parse, did_error_scanning_files

    @classmethod
    def _get_env(cls):
        """
        Extracts the environment PYTHONPATH and appends the current sys.path to those.
        """
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        return env

    def my_lint(self, filename, options=()):
        """
        This and _gen_env were ripped off from the lint.lint() function wholesale, to provide
        for a more usable interface
        """
        # traverse downwards until we are out of a python package
        if False:
            full_path = osp.abspath(filename)
            parent_path = osp.dirname(full_path)
            child_path = osp.basename(full_path)

            while parent_path != "/" and osp.exists(
                osp.join(parent_path, "__init__.py")
            ):
                child_path = osp.join(osp.basename(parent_path), child_path)
                parent_path = osp.dirname(parent_path)
        else:
            xx = filename.rindex("/")
            # print("xx-->" + str(xx))
            if xx == -1 or True:
                child_path = filename.replace("/", "\\")
                parent_path = "."
            else:
                child_path = filename[xx + 1 :]
                parent_path = filename[0:xx]
            # print("pp-->" + str(parent_path))
            parent_path = osp.abspath(parent_path)

        # Start pylint, ensuring that we use the python and pylint associated
        # with the running epylint
        run_cmd = "import sys; from pylint.lint import Run; Run(sys.argv[1:])"
        # print("cp-->" + str(child_path))
        # print("pp-->" + str(parent_path))
        cmd = [
            sys.executable,
            "-c",
            run_cmd,
            "--msg-template",
            "{line}: {symbol}",
            "-r",
            "n",
            child_path,
        ] + list(options)
        return self.__quack(cmd, parent_path)

    def __quack(self, cmd, parent_path):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=parent_path,
            env=self._get_env(),
            universal_newlines=True,
        )

        poll_return_code = process.poll()
        while poll_return_code is None:
            time.sleep(0.1)
            poll_return_code = process.poll()

        found_suppressions = []
        for line in process.stdout:

            # Remove pylintrc warning
            if line.startswith("No config file found") or line.startswith("*"):
                continue

            # modify the file name thats output to reverse the path traversal we made
            parts = line.split(":")
            found_suppressions.append(parts)

        return process.returncode, found_suppressions

    @classmethod
    def __remove_pylint_suppress_lines(cls, content_lines, start_line, end_line):
        modified_content = content_lines[:]
        modified_content[start_line] = ""
        modified_content[end_line] = ""

        last_line_index = len(modified_content) - 1
        last_line = modified_content[last_line_index]
        if last_line.endswith("\n"):
            last_line = last_line[0:-1].strip()

        # Remove any trailing blank lines
        while not last_line:
            new_last_line = modified_content[last_line_index - 1]
            if new_last_line.endswith("\n"):
                new_last_line = new_last_line[0:-1].strip()
            if not new_last_line:
                del modified_content[-1]
            last_line_index -= 1
            last_line = new_last_line

        new_last_line = modified_content[-1].strip()
        if not new_last_line and modified_content[-2].endswith("\n"):
            del modified_content[-1]
        return modified_content

    def __validate_original_scans_cleanly(self, next_file, options):

        print(f"Verifying {next_file} scans cleanly without modifications.")
        scan_return_code, found_suppressions = self.my_lint(next_file, options=options)
        if scan_return_code:

            unique_found_suppressions = []
            for next_item in found_suppressions:
                next_item = next_item[1].strip()
                if next_item not in unique_found_suppressions:
                    unique_found_suppressions.append(next_item)
            unique_found_suppressions.sort()

            suppressions_report = ""
            for next_item in enumerate(unique_found_suppressions):
                if next_item[0]:
                    suppressions_report += ", "
                suppressions_report += next_item[1]

            print(
                f"  Baseline PyLint scan found unsuppressed warnings: {suppressions_report}"
            )
            print("  Fix all errors before scanning again.")
        return scan_return_code

    # pylint: disable=too-many-arguments
    def __scan_modified_file(
        self, content_lines, logged_properties, next_file, new_file_name, options
    ):

        start_line = int(logged_properties[0]) - 1
        end_line = int(logged_properties[1]) - 1

        modified_content = self.__remove_pylint_suppress_lines(
            content_lines, start_line, end_line
        )
        self.__emit_scan_item_header(next_file, logged_properties)

        modified_content_return_code = 1
        modified_suppressions = None
        try:
            with open(new_file_name, "wt", encoding="utf-8") as outfile:
                outfile.writelines(modified_content)

            modified_content_return_code, modified_suppressions = self.my_lint(
                new_file_name, options=options
            )
            if modified_content_return_code and modified_content_return_code in [
                1,
                32,
            ]:
                translated_error_name = (
                    "Fatal Error"
                    if modified_content_return_code == 1
                    else "Usage Error"
                )
                if self.__verbose_mode:
                    print(
                        f"    Modified file scan of {next_file} failed: {translated_error_name}"
                    )
                else:
                    print(f"    Modified file scan failed: {translated_error_name}")
            else:
                modified_content_return_code = 0
        finally:
            if os.path.exists(new_file_name):
                os.remove(new_file_name)

        return modified_content_return_code, modified_suppressions

    # pylint: enable=too-many-arguments

    @classmethod
    def __search_for_suppression_in_returned_list(
        cls, logged_properties, modified_suppressions
    ):

        did_match = False
        suppression_to_test = logged_properties[2]
        for next_item in modified_suppressions:
            next_item = next_item[1].strip()
            if next_item == suppression_to_test:
                did_match = True
                break
        return did_match

    def __emit_scan_item_header(self, next_file, logged_properties):

        if self.__verbose_mode:
            print(
                f"  Verifying suppression '{logged_properties[2]}' from file {next_file}, line {logged_properties[0]-1}"
            )

    def __emit_dot_tracker_header(self, disable_enabled_log):

        if not self.__is_being_piped and not self.__verbose_mode:
            suppression_count = len(disable_enabled_log)
            print("  ", end="")
            print("".rjust(suppression_count, "."), end="")
            print("".rjust(suppression_count, "\b"), end="", flush=True)

    def __emit_dot_tracker_item(self, did_match):
        if not self.__is_being_piped and not self.__verbose_mode:
            print("v" if did_match else "U", end="", flush=True)

    def __emit_dot_tracker_footer(self, unused_suppression_tuples):
        if not self.__is_being_piped and not self.__verbose_mode:
            print(
                f" - {len(unused_suppression_tuples)} Found"
                if unused_suppression_tuples
                else ""
            )

    # pylint: disable=too-many-locals
    def __scan_file_for_unused_suppressions(
        self, disable_enabled_log, next_file, content_lines, args
    ):

        options = ["--score=n"]
        if args.config_file:
            options.append(f"--rcfile={args.config_file}")

        if self.__validate_original_scans_cleanly(next_file, options):
            return 1, None

        last_slash_index = next_file.rfind("/")
        assert last_slash_index != -1
        new_file_name = (
            next_file[0:last_slash_index] + "/__" + next_file[last_slash_index + 1 :]
        )

        self.__emit_dot_tracker_header(disable_enabled_log)

        unused_suppression_tuples = []
        last_modified_suppressions = None
        last_logged_properties = (None, None)
        for _, logged_properties in enumerate(disable_enabled_log, start=1):

            if (
                last_logged_properties
                and last_logged_properties[0] == logged_properties[0]
                and last_logged_properties[1] == logged_properties[1]
            ):
                modified_suppressions = last_modified_suppressions
                self.__emit_scan_item_header(next_file, logged_properties)
            else:
                (
                    modified_scan_return_code,
                    modified_suppressions,
                ) = self.__scan_modified_file(
                    content_lines, logged_properties, next_file, new_file_name, options
                )
            if modified_scan_return_code:
                if not self.__is_being_piped and not self.__verbose_mode:
                    print("")
                return 1, None

            last_modified_suppressions = modified_suppressions
            last_logged_properties = logged_properties

            did_match = self.__search_for_suppression_in_returned_list(
                logged_properties, modified_suppressions
            )
            if not did_match:
                start_line = int(logged_properties[0]) - 1
                suppression_to_test = logged_properties[2]
                new_tuple = (next_file, start_line, suppression_to_test)
                unused_suppression_tuples.append(new_tuple)

            self.__emit_dot_tracker_item(did_match)

        self.__emit_dot_tracker_footer(unused_suppression_tuples)
        return 0, sorted(
            unused_suppression_tuples,
            key=lambda x: x[0] + ":" + str(x[1]).rjust(7, "0"),
        )

    # pylint: enable=too-many-locals

    def __initialize_logging(self, args):
        base_logger = logging.getLogger()
        self.__new_handler = None
        if args.log_file:
            self.__new_handler = logging.FileHandler(args.log_file)
            self.__new_handler.setLevel(
                PyLintUtils.__available_log_maps[args.log_level]
            )
            base_logger.addHandler(self.__new_handler)
        else:
            base_logger.setLevel(PyLintUtils.__available_log_maps[args.log_level])

    def __terminate_logging(self):
        if self.__new_handler:
            self.__new_handler.close()

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

    def __create_report(self, args, disabled_by_file_name_map):
        return_code = 0

        entire_map = self.__create_report_map(disabled_by_file_name_map)

        try:
            with open(args.report_file, "wt", encoding="utf-8") as outfile:
                json.dump(entire_map, outfile, indent=4)
        except IOError as ex:
            return_code = 1
            assert False, f"Test configuration file was not written ({ex})."
        return return_code

    def __analyze_python_files_for_pylint_comments(self, args, files_to_scan):

        disabled_by_file_name_map = {}
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
            disabled_by_file_name_map[next_file] = disable_count_map

            if not error_count:
                self.__scan_map[next_file] = (disable_enabled_log, python_file_content)
                if args.verbose_mode:
                    print(f"  File contains {error_count} scan errors.")

        return total_error_count, disabled_by_file_name_map

    # pylint: disable=consider-using-dict-items
    def __verify_pylint_suppressions(self, args):

        return_code = 0
        all_unused_suppression_tuples = []
        for next_file in self.__scan_map:
            disable_enabled_log_for_file, python_file_content = self.__scan_map[
                next_file
            ]
            if disable_enabled_log_for_file and len(disable_enabled_log_for_file) > 0:

                # TODO replace this with proper handling.
                next_file = next_file.replace("\\", "/")

                (
                    this_return_code,
                    unused_suppression_tuples,
                ) = self.__scan_file_for_unused_suppressions(
                    disable_enabled_log_for_file, next_file, python_file_content, args
                )
                return_code = max(this_return_code, return_code)
                if unused_suppression_tuples:
                    all_unused_suppression_tuples.extend(unused_suppression_tuples)
            elif self.__verbose_mode:
                print(f"File {next_file} does not contain any PyLint suppressions.")

        if all_unused_suppression_tuples:
            print(
                f"\n{len(all_unused_suppression_tuples)} unused PyLint suppressions found."
            )
            for i in all_unused_suppression_tuples:
                print(f"{i[0]}:{i[1]}: Unused suppression: {i[2]}")
            return_code = 2
        else:
            print("\nNo unused PyLint suppressions found.")
        return return_code

    # pylint: enable=consider-using-dict-items

    def main(self):
        """
        Main entrance point.
        """
        args = self.__parse_arguments()
        self.__verbose_mode = args.verbose_mode
        self.__is_being_piped = not sys.stdout.isatty()

        return_code = 0
        try:
            self.__initialize_logging(args)

            files_to_scan, error_scanning_files = self.__determine_files_to_scan(
                args.paths
            )
            total_error_count = 0
            if error_scanning_files:
                print("No Python files found to scan.")
                return_code = 1
            elif args.list_files:
                return_code = self.__handle_list_files(files_to_scan)
            else:
                try:
                    (
                        total_error_count,
                        disabled_by_file_name_map,
                    ) = self.__analyze_python_files_for_pylint_comments(
                        args, files_to_scan
                    )
                    if total_error_count:
                        print(
                            f"\nScanned python files contained {total_error_count} PyLint suppression error(s)."
                        )
                        return_code = 1
                    elif args.report_file:
                        return_code = self.__create_report(
                            args, disabled_by_file_name_map
                        )
                    elif args.scan_suppressions:
                        return_code = self.__verify_pylint_suppressions(args)
                except KeyboardInterrupt:
                    pass
        finally:
            self.__terminate_logging()
        sys.exit(return_code)


# pylint: enable=too-many-instance-attributes


if __name__ == "__main__":
    PyLintUtils().main()
