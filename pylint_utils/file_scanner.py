"""
Module to provide for an easy manner in which to collect files to process.
"""

import glob
import logging
import os
import sys

LOGGER = logging.getLogger(__name__)


class FileScanner:
    """
    Class to provide for an easy manner in which to collect files to process.
    """

    @staticmethod
    def add_standard_arguments(parser, add_list_files_argument=False):
        """
        Add any required arguments for scanning for files to the command line.
        """

        if add_list_files_argument:
            parser.add_argument(
                "--list-files",
                dest="list_files",
                action="store_true",
                default=False,
                help="list the files found and exit",
            )

        parser.add_argument(
            "--recurse",
            dest="recurse_directories",
            action="store_true",
            default=False,
            help="recursively scan directories",
        )
        parser.add_argument(
            "--ignore-path",
            dest="ignore_path",
            action="append",
            default=None,
            help="one or more paths to ignore",
        )
        parser.add_argument(
            "paths",
            metavar="path",
            type=str,
            nargs="+",
            help="One or more paths to scan for eligible files",
        )

    @classmethod
    def __is_file_eligible_to_scan(cls, path_to_test):
        """
        Determine if the presented path is one that we want to scan.
        """
        return path_to_test.endswith(".py")

    def __process_next_path_directory(
        self, next_path, files_to_parse, recurse_directories
    ):
        LOGGER.debug("Provided path '%s' is a directory. Walking directory.", next_path)
        normalized_next_path = next_path.replace("\\", "/")
        for root, _, files in os.walk(next_path):
            normalized_root = root.replace("\\", "/")
            if not recurse_directories and normalized_root != normalized_next_path:
                continue
            normalized_root = (
                normalized_root[:-1]
                if normalized_root.endswith("/")
                else normalized_root
            )
            for file in files:
                rooted_file_path = f"{normalized_root}/{file}"
                if self.__is_file_eligible_to_scan(rooted_file_path):
                    files_to_parse.add(rooted_file_path)

    def __process_next_path(
        self, next_path, files_to_parse, recurse_directories, ignore_bad_matches
    ):

        did_find_any = False
        LOGGER.info("Determining files to scan for path '%s'.", next_path)
        if not os.path.exists(next_path):
            print(
                f"Provided path '{next_path}' does not exist.",
                file=sys.stderr,
            )
            LOGGER.debug("Provided path '%s' does not exist.", next_path)
        elif os.path.isdir(next_path):
            self.__process_next_path_directory(
                next_path, files_to_parse, recurse_directories
            )
            did_find_any = True
        elif self.__is_file_eligible_to_scan(next_path):
            LOGGER.debug(
                "Provided path '%s' is a valid file. Adding.",
                next_path,
            )
            files_to_parse.add(next_path)
            did_find_any = True
        elif ignore_bad_matches:
            LOGGER.debug(
                "Provided path '%s' is not a valid file. Skipping.",
                next_path,
            )
        else:
            LOGGER.debug(
                "Provided path '%s' is not a valid file.",
                next_path,
            )
            print(
                f"Provided file path '{next_path}' is not a valid file.",
                file=sys.stderr,
            )
        return did_find_any

    @classmethod
    def __remove_ignored_paths(cls, ignore_paths, files_to_parse):
        ignore_items = []
        for next_path in ignore_paths:
            if next_path in files_to_parse:
                ignore_items.append(next_path)
            else:
                next_path_as_directory = (
                    next_path + "/"
                    if not (next_path.endswith("/") or next_path.endswith("\\"))
                    else next_path
                )
                next_path_as_directory = next_path_as_directory.replace("\\", "/")

                for next_file_path in files_to_parse:
                    if next_file_path.startswith(next_path_as_directory):
                        ignore_items.append(next_file_path)
        for next_path_to_ignore in ignore_items:
            if next_path_to_ignore in files_to_parse:
                list_index = files_to_parse.index(next_path_to_ignore)
                del files_to_parse[list_index]

    def determine_files_to_scan(self, args):
        """
        Scan through the specified paths for any eligible files.
        """

        eligible_paths, ignore_paths, recurse_directories = (
            args.paths,
            args.ignore_path,
            args.recurse_directories,
        )

        did_error_scanning_files = False
        files_to_parse = set()
        for next_path in eligible_paths:
            if "*" in next_path or "?" in next_path:
                LOGGER.debug("Path '%s' is a glob.", next_path)
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
                    self.__process_next_path(
                        next_globbed_path, files_to_parse, recurse_directories, True
                    )
            else:
                LOGGER.debug("Path '%s' is a normal file path.", next_path)
                if not self.__process_next_path(
                    next_path, files_to_parse, recurse_directories, False
                ):
                    did_error_scanning_files = True
                    break

        files_to_parse = list(files_to_parse)
        files_to_parse.sort()

        if ignore_paths:
            self.__remove_ignored_paths(ignore_paths, files_to_parse)

        LOGGER.info("Number of files found: %s", str(len(files_to_parse)))
        return files_to_parse, did_error_scanning_files

    @staticmethod
    def handle_list_files_if_argument_present(args, files_to_scan):
        """
        If the `add_standard_arguments` function added a list files argument and it was
        set, then process.  Otherwise return None.
        """

        if not args.list_files:
            return None

        if files_to_scan:
            print("\n".join(files_to_scan))
            return 0

        print("No matching files found.", file=sys.stderr)
        return 1
