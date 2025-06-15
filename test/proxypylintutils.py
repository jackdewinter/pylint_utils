"""
Module to provide for a local instance of an InProcessExecution class.
"""

import os
import sys
from test.pytest_execute import InProcessExecution
from typing import List, Optional

# https://docs.pytest.org/en/latest/goodpractices.html#tests-outside-application-code
sys.path.insert(0, os.path.abspath("pylint_utils"))  # isort:skip
# pylint: disable=wrong-import-position
from pylint_utils.main import PyLintUtils  # isort:skip
from pylint_utils.__main__ import main

# pylint: enable=wrong-import-position


class ProxyPyLintUtils(InProcessExecution):
    """
    Class to provide for a local instance of an InProcessExecution class.
    """

    def __init__(self, use_module: bool = False, use_main: bool = False) -> None:
        super().__init__()
        self.__use_main = use_main

        self.__entry_point = "__main.py__" if use_module else "main.py"
        resource_directory = os.path.join(os.getcwd(), "test", "resources")
        assert os.path.exists(resource_directory)
        assert os.path.isdir(resource_directory)
        self.resource_directory = resource_directory

    def execute_main(self, direct_arguments: Optional[List[str]] = None) -> None:
        if self.__use_main:
            main()
        else:
            PyLintUtils().main()

    def get_main_name(self) -> str:
        return self.__entry_point
