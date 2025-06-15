"""
Module to provide for a simple bootstrap for the project.
"""

from pylint_utils.main import PyLintUtils


class Main:
    """
    Class to provide for a simple bootstrap for the project.
    """

    def main(self) -> None:
        """
        Main entrance point.
        """
        PyLintUtils().main()


if __name__ == "__main__":
    Main().main()
