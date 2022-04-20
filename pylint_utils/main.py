"""
Module to ...
"""


import argparse
import contextlib
import logging
import os
import os.path as osp
import runpy
import subprocess
import sys
import time

from pylint_utils.file_scanner import FileScanner
from pylint_utils.pylint_comment_scanner import PyLintCommentScanner
from pylint_utils.simple_logging import SimpleLogging

LOGGER = logging.getLogger(__name__)


class PyLintUtils:
    """
    Class to provide for...
    """

    __default_log_level = "CRITICAL"

    def __init__(self):
        self.__version_number = PyLintUtils.__get_semantic_version()
        self.__verbose_mode = None
        self.__display_progress = None

    @staticmethod
    def __get_semantic_version():
        file_path = __file__
        assert os.path.isabs(file_path)
        file_path = file_path.replace(os.sep, "/")
        last_index = file_path.rindex("/")
        file_path = f"{file_path[: last_index + 1]}version.py"
        version_meta = runpy.run_path(file_path)
        return version_meta["__version__"]

    def __parse_arguments(self):
        parser = argparse.ArgumentParser(
            description="Analyze any found Python files for PyLint suppressions."
        )
        parser.add_argument(
            "--verbose",
            dest="verbose_mode",
            action="store_true",
            default=False,
            help="show lots of stuff",
        )
        parser.add_argument(
            "--version", action="version", version=f"{self.__version_number}"
        )

        SimpleLogging.add_standard_arguments(parser, PyLintUtils.__default_log_level)

        parser.add_argument(
            "--x-display",
            dest="x_test_display",
            action="store_true",
            default="",
            help=argparse.SUPPRESS,
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

        FileScanner.add_standard_arguments(parser, add_list_files_argument=True)

        return parser.parse_args()

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
        # TODO traverse downwards until we are out of a python package
        # OR
        # have command line specify the actual root to use, overriding all this.
        # if False:
        #     full_path = osp.abspath(filename)
        #     parent_path = osp.dirname(full_path)
        #     child_path = osp.basename(full_path)

        #     while parent_path != "/" and osp.exists(
        #         osp.join(parent_path, "__init__.py")
        #     ):
        #         child_path = osp.join(osp.basename(parent_path), child_path)
        #         parent_path = osp.dirname(parent_path)
        # else:
        # xx = filename.rindex("/")
        # print("xx-->" + str(xx))
        # if xx == -1 or True:
        if sys.platform.startswith("win"):
            child_path = filename.replace("/", "\\")
        else:
            child_path = filename
        parent_path = "."
        # else:
        #     child_path = filename[xx + 1 :]
        #     parent_path = filename[0:xx]
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

    # pylint: disable=broad-except
    def __quack(self, cmd, parent_path):
        return_code = -1
        try:
            with subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=parent_path,
                env=self._get_env(),
                universal_newlines=True,
            ) as process:

                poll_return_code = process.poll()
                while poll_return_code is None:
                    time.sleep(0.1)
                    poll_return_code = process.poll()

                found_suppressions = []
                was_any_fatal = False
                for line in process.stdout:
                    # print("out:" + line + ":")

                    # Remove pylintrc warning
                    if line.startswith("No config file found") or line.startswith("*"):
                        continue

                    # modify the file name thats output to reverse the path traversal we made
                    parts = line.split(":")
                    if not was_any_fatal:
                        was_any_fatal = (
                            parts[0].lower() == "fatal" or parts[1].lower() == "fatal"
                        )
                    found_suppressions.append(parts)

                # if was_any_fatal:
                #     print(f"Pylint returned a fatal error:{process.returncode}")
                # else:
                #     print(f"Pylint returned normal:{process.returncode}:{cmd}")
                # for line in process.stdout:
                #     print("out:" + line + ":")
                # for line in process.stderr:
                #     print("err:" + line + ":")
                return_code = process.returncode
        except Exception as exception:
            print(f"Pylint returned exception:{exception}")
        # print(f"cmd:{cmd}:")
        # print(f"return_code:{return_code}:")
        # print(f"found_suppressions:{found_suppressions}:")
        return return_code, found_suppressions

    # pylint: enable=broad-except

    @classmethod
    def __remove_pylint_suppress_lines(cls, content_lines, start_line, end_line):
        modified_content = content_lines[:]
        modified_content[start_line] = ""
        modified_content[end_line] = ""

        last_line_index = len(modified_content) - 1
        last_line = modified_content[last_line_index]
        if last_line.endswith("\n"):
            last_line = last_line[:-1].strip()

        # Remove any trailing blank lines
        while not last_line:
            new_last_line = modified_content[last_line_index - 1]
            if new_last_line.endswith("\n"):
                new_last_line = new_last_line[:-1].strip()
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
                f"  Verifying suppression '{logged_properties[2]}' from file {next_file}, line {logged_properties[0]}"
            )

    def __emit_dot_tracker_header(self, disable_enabled_log):

        if self.__display_progress:
            suppression_count = len(disable_enabled_log)
            print("  ", end="")
            print("".rjust(suppression_count, "."), end="")
            print("".rjust(suppression_count, "\b"), end="", flush=True)

    def __emit_dot_tracker_item(self, did_match):
        if self.__display_progress:
            print("v" if did_match else "U", end="", flush=True)

    def __emit_dot_tracker_footer(self, unused_suppression_tuples):
        if self.__display_progress:
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
            f"{next_file[:last_slash_index]}/__{next_file[last_slash_index + 1 :]}"
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
                if self.__display_progress:
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
            key=lambda x: f"{x[0]}:" + str(x[1]).rjust(7, "0"),
        )

    # pylint: enable=too-many-locals

    def __verify_pylint_suppressions(self, args, pylint_scanner):

        return_code = 0
        all_unused_suppression_tuples = []
        for next_file in pylint_scanner.scan_map:
            disable_enabled_log_for_file, python_file_content = pylint_scanner.scan_map[
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
                print(f"{i[0]}:{i[1]+1}: Unused suppression: {i[2]}")
            return_code = 2
        else:
            print("\nNo unused PyLint suppressions found.")
        return return_code

    def __process_files_to_scan(self, args, files_to_scan):
        return_code = 0
        with contextlib.suppress(KeyboardInterrupt):
            pylint_scanner = PyLintCommentScanner()
            if total_error_count := pylint_scanner.analyze_python_files_for_pylint_comments(
                args, files_to_scan
            ):
                print(
                    f"\nScanned python files contained {total_error_count} PyLint suppression error(s)."
                )
                return_code = 1
            elif args.report_file:
                return_code = pylint_scanner.create_report(args)
            elif args.scan_suppressions:
                return_code = self.__verify_pylint_suppressions(args, pylint_scanner)
        return return_code

    def main(self):
        """
        Main entrance point.
        """
        args = self.__parse_arguments()
        self.__verbose_mode = args.verbose_mode
        self.__display_progress = (
            sys.stdout.isatty() or args.x_test_display
        ) and not self.__verbose_mode

        return_code = 0
        try:
            SimpleLogging.initialize_logging(args)

            files_to_scan, error_scanning_files = FileScanner().determine_files_to_scan(
                args
            )
            if error_scanning_files:
                return_code = 1
            else:
                return_code = FileScanner.handle_list_files_if_argument_present(
                    args, files_to_scan
                )
                if return_code is None:
                    return_code = self.__process_files_to_scan(args, files_to_scan)
        finally:
            SimpleLogging.terminate_logging()
        sys.exit(return_code)


if __name__ == "__main__":
    PyLintUtils().main()
