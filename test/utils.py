"""
Module to provide helper methods for tests.
"""
import difflib
import json
import tempfile


def write_temporary_configuration(supplied_configuration):
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
        assert False, f"Test configuration file was not written ({ex})."


@staticmethod
def make_string_visible(expected_string):
    return expected_string.replace("\n", "\\n")


def assert_if_strings_different(expected_string, actual_string):
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
