"""
Module to provide tests related to the basic parts of the scanner.
"""
import runpy
from test.pylintutils import ProxyPyLintUtils


def test_markdown_with_dash_dash_version():
    """
    Test to make sure we get the correct response if 'version' is supplied.
    """

    # Arrange
    scanner = ProxyPyLintUtils()
    supplied_arguments = ["--version"]

    version_meta = runpy.run_path("./pylint_utils/version.py")
    semantic_version = version_meta["__version__"]

    expected_return_code = 0
    expected_output = """{version}
""".replace(
        "{version}", semantic_version
    )
    expected_error = ""

    # Act
    execute_results = scanner.invoke_main(arguments=supplied_arguments)

    # Assert
    execute_results.assert_results(
        expected_output, expected_error, expected_return_code
    )
