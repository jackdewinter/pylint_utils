"""
Module to provide tests related to
"""

import json
import os
import tempfile
from test.patch_builtin_open import PatchBuiltinOpen
from test.proxypylintutils import ProxyPyLintUtils
from test.pytest_execute import InProcessExecution

from project_summarizer.main import ProjectSummarizer


class ProxyProjectSummarizer(InProcessExecution):
    """
    Class to provide for a local instance of an InProcessExecution class.
    """

    def __init__(self, use_module=False, use_main=False):
        super().__init__()
        _ = use_main, use_module

    def execute_main(self):
        ProjectSummarizer().main()

    def get_main_name(self):
        return "bob"


def __generate_report_file(
    file_to_scan, report_file_name, report_directory, publish_directory=None
):
    scanner = ProxyPyLintUtils()
    supplied_arguments = [
        "--report",
        report_file_name,
        file_to_scan,
    ]
    execute_results = scanner.invoke_main(arguments=supplied_arguments)
    assert not execute_results.return_code

    if publish_directory:
        scanner = ProxyProjectSummarizer()
        supplied_arguments = [
            "--add-plugin",
            "pylint_utils/pylint_suppression_summarizer_plugin.py",
            "--report-dir",
            report_directory,
            "--publish-dir",
            publish_directory,
            "--pylint-suppressions",
            report_file_name,
        ]
        execute_results = scanner.invoke_main(arguments=supplied_arguments)
        assert not execute_results.return_code

        scanner = ProxyProjectSummarizer()
        supplied_arguments = [
            "--add-plugin",
            "pylint_utils/pylint_suppression_summarizer_plugin.py",
            "--report-dir",
            report_directory,
            "--publish-dir",
            publish_directory,
            "--publish",
        ]
        execute_results = scanner.invoke_main(arguments=supplied_arguments)
        assert not execute_results.return_code


def test_project_summarizer_base_report():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                )

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                ]

                expected_return_code = 0
                expected_output = """PyLint Suppression Summary
---------------------


  SUPPRESSION         COUNT  DELTA

  too-many-arguments      1     +1


"""
                expected_error = ""

                # Act
                execute_results = scanner.invoke_main(arguments=supplied_arguments)

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)


def test_project_summarizer_base_report_with_same_publish():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                    temporary_publish_directory,
                )

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                ]

                expected_return_code = 0
                expected_output = """PyLint Suppression Summary
---------------------


  SUPPRESSION         COUNT  DELTA

  too-many-arguments      1      0


"""
                expected_error = ""

                # Act
                execute_results = scanner.invoke_main(arguments=supplied_arguments)

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)


def test_project_summarizer_base_report_with_same_publish_x():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                    temporary_publish_directory,
                )
                __generate_report_file(
                    "test/resources/clean_file.py",
                    report_file_name,
                    temporary_report_directory,
                )

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                ]

                expected_return_code = 0
                expected_output = """PyLint Suppression Summary
---------------------


  SUPPRESSION         COUNT  DELTA

  too-many-arguments      0     -1


"""
                expected_error = ""

                # Act
                execute_results = scanner.invoke_main(arguments=supplied_arguments)

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)


def test_project_summarizer_base_report_with_same_publish_only_changes():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                    temporary_publish_directory,
                )

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                    "--only-changes",
                ]

                expected_return_code = 0
                expected_output = """PyLint Suppression Summary
---------------------

PyLint suppressions have not changed since last published suppressions.

"""
                expected_error = ""

                # Act
                execute_results = scanner.invoke_main(arguments=supplied_arguments)

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)


def test_project_summarizer_base_report_with_same_publish_quiet():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                    temporary_publish_directory,
                )

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                    "--quiet",
                ]

                expected_return_code = 0
                expected_output = ""
                expected_error = ""

                # Act
                execute_results = scanner.invoke_main(arguments=supplied_arguments)

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)


def test_project_summarizer_bad_1():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w+") as temp_file:
                report_file_name = temp_file.name
                report_dictionary = {}
                json.dump(report_dictionary, temp_file.file)

            scanner = ProxyProjectSummarizer()
            supplied_arguments = [
                "--add-plugin",
                "pylint_utils/pylint_suppression_summarizer_plugin.py",
                "--report-dir",
                temporary_report_directory,
                "--pylint-suppressions",
                report_file_name,
            ]

            expected_return_code = 1
            expected_output = ""
            expected_error = (
                "Report file does not appear to be a pylint_utils generated file."
            )

            # Act
            execute_results = scanner.invoke_main(arguments=supplied_arguments)

            # Assert
            execute_results.assert_results(
                expected_output, expected_error, expected_return_code
            )
        finally:
            if os.path.exists(report_file_name):
                os.remove(report_file_name)


def test_project_summarizer_bad_2():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        try:
            with tempfile.NamedTemporaryFile(delete=False, mode="w+") as temp_file:
                report_file_name = temp_file.name
                temp_file.file.write("this is not json")

            scanner = ProxyProjectSummarizer()
            supplied_arguments = [
                "--add-plugin",
                "pylint_utils/pylint_suppression_summarizer_plugin.py",
                "--report-dir",
                temporary_report_directory,
                "--pylint-suppressions",
                report_file_name,
            ]

            expected_return_code = 1
            expected_output = ""
            expected_error = "File error reading report file as a json file: Expecting value: line 1 column 1 (char 0)"

            # Act
            execute_results = scanner.invoke_main(arguments=supplied_arguments)

            # Assert
            execute_results.assert_results(
                expected_output, expected_error, expected_return_code
            )
        finally:
            if os.path.exists(report_file_name):
                os.remove(report_file_name)


def test_project_summarizer_bad_3():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        scanner = ProxyProjectSummarizer()
        supplied_arguments = [
            "--add-plugin",
            "pylint_utils/pylint_suppression_summarizer_plugin.py",
            "--report-dir",
            temporary_report_directory,
            "--pylint-suppressions",
            temporary_report_directory,
        ]

        expected_return_code = 1
        expected_output = ""
        expected_error = "File error opening report file: [Errno 13] Permission denied:"
        additional_error = ["\n"]

        # Act
        execute_results = scanner.invoke_main(arguments=supplied_arguments)

        # Assert
        execute_results.assert_results(
            expected_output,
            expected_error,
            expected_return_code,
            additional_error=additional_error,
        )


def test_project_summarizer_bad_4():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                )

                publish_path = os.path.join(
                    temporary_publish_directory, "pylint_suppression.json"
                )
                with open(publish_path, mode="wt", encoding="utf-8") as write_file:
                    write_file.write("not a json file")

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                ]

                expected_return_code = 1
                expected_output = ""
                expected_error = (
                    f"Previous coverage summary file '{publish_path}' is not "
                    + "a valid JSON file (Expecting value: line 1 column 1 (char 0))."
                )

                # Act
                execute_results = scanner.invoke_main(arguments=supplied_arguments)

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)


def test_project_summarizer_bad_5():
    """
    Test to make sure that the plugin can generate a basic report.
    """

    # Arrange
    with tempfile.TemporaryDirectory() as temporary_report_directory:
        with tempfile.TemporaryDirectory() as temporary_publish_directory:
            try:
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    report_file_name = temp_file.name

                __generate_report_file(
                    "test/resources/balanced_file.py",
                    report_file_name,
                    temporary_report_directory,
                )

                publish_path = os.path.join(
                    temporary_publish_directory, "pylint_suppression.json"
                )
                with open(publish_path, mode="wt", encoding="utf-8") as write_file:
                    write_file.write("not a json file")

                scanner = ProxyProjectSummarizer()
                supplied_arguments = [
                    "--add-plugin",
                    "pylint_utils/pylint_suppression_summarizer_plugin.py",
                    "--report-dir",
                    temporary_report_directory,
                    "--publish-dir",
                    temporary_publish_directory,
                    "--pylint-suppressions",
                    report_file_name,
                ]

                mock_exception_message = "fred"

                expected_return_code = 1
                expected_output = ""
                expected_error = f" Previous coverage summary file '{publish_path}' was not loaded ({mock_exception_message})."

                # Act
                try:
                    pbo = PatchBuiltinOpen()
                    pbo.register_exception(
                        publish_path, "r", exception_message=mock_exception_message
                    )
                    pbo.start()

                    execute_results = scanner.invoke_main(arguments=supplied_arguments)
                finally:
                    pbo.stop()

                # Assert
                execute_results.assert_results(
                    expected_output, expected_error, expected_return_code
                )
            finally:
                if os.path.exists(report_file_name):
                    os.remove(report_file_name)
