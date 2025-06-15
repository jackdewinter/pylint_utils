"""
Module to provide helper methods for tests.
"""

import difflib
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from io import StringIO
from typing import Any, Dict, Generator, List, Optional

import portalocker

# Name of the lock file used to indicate that the tests are running.
# This is needed as the "list" tests that look for files to scan can
# execute at the same time as the tests that create "temporary" files
# in the same directory with a `_` prefix for scanning in place.
ACTIVE_LOCK_FILE_NAME = "active-testing-pylint-utils"


def write_temporary_configuration(supplied_configuration: Any) -> str:
    """
    Write the configuration as a temporary file that is kept around.
    """
    try:
        with tempfile.NamedTemporaryFile("wt", delete=False) as outfile:
            if isinstance(supplied_configuration, str):
                outfile.write(supplied_configuration)
            else:
                json.dump(supplied_configuration, outfile)
            return outfile.name
    except IOError as ex:
        raise AssertionError(f"Test configuration file was not written ({ex}).") from ex


def make_string_visible(expected_string: str) -> str:
    """
    Simple function to make a string visible.
    """
    return expected_string.replace("\n", "\\n")


def assert_if_strings_different(expected_string: str, actual_string: str) -> None:
    """
    Compare two strings and make sure they are equal, asserting if not.
    """

    print(f"expected_string({len(expected_string)})>>{expected_string}<<")
    print(f"expected_string>>{make_string_visible(expected_string)}<<")

    print(f"actual_string  ({len(actual_string)})>>{actual_string}<<")
    print(f"actual_string  >>{make_string_visible(actual_string)}<<")

    diff = difflib.ndiff(expected_string, actual_string)

    diff_values = "\n".join(list(diff))
    diff_values = f"{diff_values}\n---\n"

    assert expected_string == actual_string, f"Strings are not equal.{diff_values}"


def __generate_lock_file_name(lock_file_name: str) -> str:
    lock_file = f"{lock_file_name}.lock"

    if os.sep not in lock_file_name:
        lock_file = os.path.join(tempfile.gettempdir(), lock_file)
    lock_file = os.path.abspath(lock_file)
    return lock_file


@contextmanager
def obtain_multiprocess_lock(lock_file_name: str) -> Generator[str, None, None]:
    """
    Obtain a lock for the given file name to prevent multiple processes from running at the same time.
    """
    lock_file = __generate_lock_file_name(lock_file_name)
    with portalocker.Lock(lock_file, mode="w+", flags=portalocker.LOCK_EX):
        yield lock_file


class PatchSubprocessProcess:
    """
    Mocked subprocess process to simulate a subprocess call that finishes immediately.
    """

    def __init__(
        self, return_code: int, stdout: str, stderr: str, countdown: int = 0
    ) -> None:
        self.__return_code = return_code
        self.__stdout = StringIO(stdout)
        self.__stderr = StringIO(stderr)
        self.__countdown = countdown

    def check_count(self) -> bool:
        """
        Check if the countdown has reached zero, indicating that the patched behavior should be in effect.
        """
        if self.__countdown <= 0:
            return True
        self.__countdown -= 1
        return False

    def __enter__(self) -> "PatchSubprocessProcess":
        """
        Enter method for the context manager, does nothing."""
        return self

    def __exit__(self, exc_type: int, value: int, traceback: int) -> None:
        """
        Exit method for the context manager, does nothing.
        """

    def poll(self) -> int:
        """
        Provide an interface to the poll method of the subprocess that finishes right away with the specified return code.
        """
        return self.__return_code

    @property
    def returncode(self) -> int:
        """
        Return the return code of the process.
        """
        return self.__return_code

    @property
    def stdout(self) -> StringIO:
        """
        Return the stdout output of the process.
        """
        return self.__stdout

    @property
    def stderr(self) -> StringIO:
        """
        Return the stderr output of the process.
        """
        return self.__stderr


class PatchSubprocessPopen:
    """
    Patch for a subprocess call to mock out the response.
    """

    def __init__(self, mock_process: Optional[PatchSubprocessProcess] = None) -> None:
        self.mock_patcher = None
        self.patched_open = None
        self.__process_result = mock_process

    def start(self) -> None:
        """
        Start the patching of the "open" function.
        """
        self.mock_patcher = unittest.mock.patch("subprocess.Popen")  # type: ignore
        self.patched_open = self.mock_patcher.start()  # type: ignore
        self.patched_open.side_effect = self.__my_popen  # type: ignore

    def stop(self) -> None:
        """
        Stop the patching of the "open" function.
        """
        self.mock_patcher.stop()  # type: ignore
        self.mock_patcher = None

    def __my_popen(self, *args: List[Any], **kwargs: Dict[str, Any]) -> Any:
        """
        Mock out the opening of another process.
        """

        popen_commands = args[0]
        rt_index = popen_commands.index("-r")
        file_name = popen_commands[rt_index + 2]
        if self.__process_result and self.__process_result.check_count():
            return self.__process_result
        if os.path.basename(file_name).startswith("__"):
            raise IOError("goober")
        try:
            self.mock_patcher.stop()  # type: ignore

            return subprocess.Popen(  # type: ignore
                *args,
                **kwargs,
            )
        finally:
            self.patched_open = self.mock_patcher.start()  # type: ignore
            self.patched_open.side_effect = self.__my_popen  # type: ignore
