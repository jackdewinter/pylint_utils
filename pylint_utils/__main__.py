"""
Module to provide for "-m pylintutils" access to the module,
as if it was run from the console.
"""
from pylint_utils.main import PyLintUtils


def main():
    """
    Main entry point.  Exposed in this manner so that the setup
    entry_points configuration has something to execute.
    """
    PyLintUtils().main()


if __name__ == "__main__":
    main()
