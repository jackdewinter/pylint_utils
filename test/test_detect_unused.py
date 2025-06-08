"""
Module to provide test cases that test the verfication that pylint suppress messages
are still required.
"""

import os
import tempfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.proxypylintutils import ProxyPyLintUtils
from test.utils import (
    ACTIVE_LOCK_FILE_NAME,
    PatchSubprocessPopen,
    PatchSubprocessProcess,
    obtain_multiprocess_lock,
)


def write_temporary_configuration(pylint_config_to_disable: str) -> str:
    """
    Write the configuration as a temporary file that is kept around.
    """
    configuration_text = f"[pylint]\ndisable = {pylint_config_to_disable}\n"
    try:
        with tempfile.NamedTemporaryFile("wt", delete=False) as outfile:
            outfile.write(configuration_text)
            return outfile.name
    except IOError as this_exception:
        raise AssertionError(
            f"Test configuration file was not written ({this_exception})."
        ) from this_exception


def test_scan_for_unused_original_not_clean() -> None:
    """
    Test to make sure that scanning a file that is not originally clean will result
    in an error right away.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-module-docstring
  Fix all errors before scanning again.
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_with_multiple_unsuppressed_in_original() -> None:
    """
    Test to make sure that scanning a file that is not originally clean on multiple
    counts will result in an error right away.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/yet_another_bad_file.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-function-docstring, missing-module-docstring, too-many-arguments
  Fix all errors before scanning again.
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_with_multiple_unsuppressed_in_original_with_config() -> None:
    """
    Test to make sure that scanning a file that is not originally clean on multiple
    counts will result in an error right away.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        warning_to_suppress = "missing-function-docstring, missing-module-docstring, too-many-arguments, trailing-newlines, too-many-positional-arguments"
        configuration_file = None
        try:
            configuration_file = write_temporary_configuration(warning_to_suppress)
            scanner = ProxyPyLintUtils()
            file_to_scan = "test/resources/yet_another_bad_file.py"
            supplied_arguments = [
                "--config",
                configuration_file,
                "--scan",
                file_to_scan,
            ]

            expected_return_code = 2
            expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file_to_scan}:5: Unused suppression: too-many-branches
"""
            expected_error = ""

            # Act
            execute_results = scanner.invoke_main(arguments=supplied_arguments)

            # Assert
            execute_results.assert_results(
                expected_output, expected_error, expected_return_code
            )
        finally:
            if configuration_file and os.path.exists(configuration_file):
                os.remove(configuration_file)


def test_scan_with_multiple_unsuppressed_in_original_with_bad_end_with_config() -> None:
    """
    Test to make sure that scanning a file that is not originally clean on multiple
    counts will result in an error right away.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        warning_to_suppress = (
            "missing-function-docstring, missing-module-docstring, "
            + "too-many-arguments, missing-final-newline, too-many-positional-arguments"
        )
        configuration_file = None
        try:
            configuration_file = write_temporary_configuration(warning_to_suppress)
            scanner = ProxyPyLintUtils()
            file_to_scan = "test/resources/yet_another_bad_file_with_bad_end.py"
            supplied_arguments = [
                "--config",
                configuration_file,
                "--scan",
                file_to_scan,
            ]

            expected_return_code = 2
            expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file_to_scan}:5: Unused suppression: too-many-branches
"""
            expected_error = ""

            # Act
            execute_results = scanner.invoke_main(arguments=supplied_arguments)

            # Assert
            execute_results.assert_results(
                expected_output, expected_error, expected_return_code
            )
        finally:
            if configuration_file and os.path.exists(configuration_file):
                os.remove(configuration_file)


def test_scan_for_unused_original_not_clean_with_verbose() -> None:
    """
    Test to make sure that scanning a file that is not originally clean will result
    in an error right away.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file.py"
        supplied_arguments = [
            "--verbose",
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = f"""Scanning file: {file_to_scan}
  File contains 0 scan errors.
Verifying {file_to_scan} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: missing-module-docstring
  Fix all errors before scanning again.
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_not_clean_with_config() -> None:
    """
    Test to make sure that scanning a file that is not originally clean, but
    clean with applied configuration, will result in a clean parsing.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        configuration_file = None
        warning_to_suppress = "missing-module-docstring"
        try:
            configuration_file = write_temporary_configuration(warning_to_suppress)
            scanner = ProxyPyLintUtils()
            file_to_scan = "test/resources/balanced_file.py"
            supplied_arguments = [
                "--config",
                configuration_file,
                "--scan",
                file_to_scan,
            ]

            expected_return_code = 0
            expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.

No unused PyLint suppressions found.
"""
            expected_error = ""

            # Act
            execute_results = scanner.invoke_main(arguments=supplied_arguments)

            # Assert
            execute_results.assert_results(
                expected_output, expected_error, expected_return_code
            )
        finally:
            if configuration_file and os.path.exists(configuration_file):
                os.remove(configuration_file)


def test_scan_for_unused_original_not_clean_with_bad_config() -> None:
    """
    Test to make sure that scanning a file that is not originally clean,
    with a bad configuration file, will result in a clean parsing.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        configuration_file = "test/resources/README.md"
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file.py"
        supplied_arguments = [
            "--config",
            configuration_file,
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = ""
        expected_stdout_parts = [
            f"""Verifying {file_to_scan} scans cleanly without modifications.
Pylint returned exception:""",
            """Fix all errors before scanning again.""",
        ]
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output,
            expected_error,
            expected_return_code,
            output_parts=expected_stdout_parts,
        )


def test_scan_for_unused_original_clean() -> None:
    """
    Test to make sure that scanning a file that is clean will result in nothing being found.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 0
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.

No unused PyLint suppressions found.
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_clean_with_verbose() -> None:
    """
    Test to make sure that scanning a file that is clean will result in nothing being found.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--verbose",
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 0
        expected_output = f""" Scanning file: test/resources/balanced_file_clean.py
  File contains 0 scan errors.
Verifying {file_to_scan} scans cleanly without modifications.
  Verifying suppression 'too-many-arguments' from file test/resources/balanced_file_clean.py, line 6

No unused PyLint suppressions found.
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_clean_with_display() -> None:
    """
    Test to make sure that scanning a file that is clean will result in nothing being found.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--x-display",
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 0
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
  .\bv

No unused PyLint suppressions found.
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_clean_with_extra_suppression_first() -> None:
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted first in the suppress line will report and extra suppression.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean_with_extra_first.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 2
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file_to_scan}:6: Unused suppression: too-many-branches
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_clean_with_extra_suppression_first_with_verbose() -> (
    None
):
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted first in the suppress line will report and extra suppression.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean_with_extra_first.py"
        supplied_arguments = [
            "--verbose",
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 2
        expected_output = f"""Scanning file: {file_to_scan}
  File contains 0 scan errors.
Verifying {file_to_scan} scans cleanly without modifications.
  Verifying suppression 'too-many-branches' from file test/resources/balanced_file_clean_with_extra_first.py, line 6
  Verifying suppression 'too-many-arguments' from file test/resources/balanced_file_clean_with_extra_first.py, line 6

1 unused PyLint suppressions found.
{file_to_scan}:6: Unused suppression: too-many-branches
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_clean_with_extra_suppression_last() -> None:
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted last in the suppress line will report and extra suppression.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean_with_extra_last.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 2
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.

1 unused PyLint suppressions found.
{file_to_scan}:6: Unused suppression: too-many-branches
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_original_clean_with_extra_suppression_last_with_verbose() -> (
    None
):
    """
    Test to make sure that scanning a file that is pylint clean with an extra
    suppression noted last in the suppress line will report and extra suppression.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean_with_extra_last.py"
        supplied_arguments = [
            "--verbose",
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 2
        expected_output = f"""Scanning file: {file_to_scan}
  File contains 0 scan errors.
Verifying {file_to_scan} scans cleanly without modifications.
  Verifying suppression 'too-many-arguments' from file test/resources/balanced_file_clean_with_extra_last.py, line 6
  Verifying suppression 'too-many-branches' from file test/resources/balanced_file_clean_with_extra_last.py, line 6

1 unused PyLint suppressions found.
{file_to_scan}:6: Unused suppression: too-many-branches
"""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_clean() -> None:
    """
    Test to make sure that scanning a file that is has not pylint suppressions.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/clean_file.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 0
        expected_output = """No unused PyLint suppressions found."""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_clean_with_verbose() -> None:
    """
    Test to make sure that scanning a file that is has not pylint suppressions.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/clean_file.py"
        supplied_arguments = [
            "--verbose",
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 0
        expected_output = f"""Scanning file: {file_to_scan}
  File contains 0 scan errors.
File {file_to_scan} does not contain any PyLint suppressions.

No unused PyLint suppressions found."""
        expected_error = ""

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_with_bad_scan_file_openx() -> None:
    """
    Test to make sure that scanning a file that fails when the new scan file
    is opened is captured properly.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_not_python.py"
        supplied_arguments = [
            "--verbose",
            "--scan",
            file_to_scan,
        ]

        test_file_to_scan_path = (
            f"{os.path.dirname(file_to_scan)}/__{os.path.basename(file_to_scan)}"
        )
        mock_exception_message = "bob"

        expected_return_code = 1
        expected_output = f"""Scanning file: {file_to_scan}
  File contains 0 scan errors.
Verifying {file_to_scan} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: syntax-error
  Fix all errors before scanning again."""
        expected_error = ""

        # Act
        pbo = None
        try:
            pbo = PatchBuiltinOpen()
            pbo.register_exception(
                test_file_to_scan_path, "wt", exception_message=mock_exception_message
            )
            pbo.start()

            execute_results = scanner.invoke_main(arguments=supplied_arguments)
        finally:
            if pbo:
                pbo.stop()

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_with_bad_scan_file_open_and_display() -> None:
    """
    Test to make sure that scanning a file that fails when the new scan file
    is opened is captured properly, with the display mode turned on.
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--x-display",
            "--scan",
            file_to_scan,
        ]

        test_file_to_scan_path = (
            f"{os.path.dirname(file_to_scan)}/__{os.path.basename(file_to_scan)}"
        )
        mock_exception_message = "bob"

        expected_return_code = 1
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
  .\b    Modified file scan of {file_to_scan} failed during creation: {mock_exception_message}

"""
        expected_error = ""

        # Act
        pbo = None
        try:
            pbo = PatchBuiltinOpen()
            pbo.register_exception(
                test_file_to_scan_path, "wt", exception_message=mock_exception_message
            )
            pbo.start()

            execute_results = scanner.invoke_main(arguments=supplied_arguments)
        finally:
            if pbo:
                pbo.stop()

        # Assert
        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_with_bad_scan_subprocess_popen_and_display() -> None:
    """
    Test to make sure that...
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
Pylint returned exception:goober
    Modified file scan of {file_to_scan} failed: Fatal Error
"""
        expected_error = ""

        # Act
        pbo = None
        try:
            pbo = PatchSubprocessPopen()
            pbo.start()

            execute_results = scanner.invoke_main(arguments=supplied_arguments)

        finally:
            if pbo is not None:
                pbo.stop()

        # Assert
        # assert mock_subproc_popen.called

        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_with_bad_scan_subprocess_popen_and_displayxx() -> None:
    """
    Test to make sure that...
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
  Baseline PyLint scan found unsuppressed warnings: too-many-arguments
  Baseline PyLint scan found reported error output: 
  ERR:err
  Fix all errors before scanning again."""
        expected_error = ""

        # Act
        pbo = None
        try:
            pbo = PatchSubprocessPopen(
                PatchSubprocessProcess(1, "6: too-many-arguments", "err")
            )
            pbo.start()

            execute_results = scanner.invoke_main(arguments=supplied_arguments)

        finally:
            if pbo is not None:
                pbo.stop()

        # Assert
        # assert mock_subproc_popen.called

        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )


def test_scan_for_unused_with_bad_scan_subprocess_popen_and_displayxxx() -> None:
    """
    Test to make sure that...
    """

    with obtain_multiprocess_lock(ACTIVE_LOCK_FILE_NAME):
        # Arrange
        scanner = ProxyPyLintUtils()
        file_to_scan = "test/resources/balanced_file_clean.py"
        supplied_arguments = [
            "--scan",
            file_to_scan,
        ]

        expected_return_code = 1
        expected_output = f"""Verifying {file_to_scan} scans cleanly without modifications.
    Modified file scan of {file_to_scan} failed: Fatal Error

    ERR:err"""
        expected_error = ""

        # Act
        pbo = None
        try:
            pbo = PatchSubprocessPopen(
                PatchSubprocessProcess(1, "6: too-many-arguments", "err", 1)
            )
            pbo.start()

            execute_results = scanner.invoke_main(arguments=supplied_arguments)

        finally:
            if pbo is not None:
                pbo.stop()

        # Assert
        # assert mock_subproc_popen.called

        execute_results.assert_results(
            expected_output, expected_error, expected_return_code
        )
