"""
Module documentation docstring.
"""


# pylint: disable=too-many-arguments
def __print_me(first, second, third, fourth, fifth, sixth, seventh):
    print(f"first={first}")
    print(f"second={second}")
    print(f"third={third}")
    print(f"fourth={fourth}")
    print(f"fifth={fifth}")
    print(f"sixth={sixth}")
    print(f"seventh={seventh}")


# pylint: enable=too-many-arguments

__print_me(1, "2", 3.0, 4, "five", 6.00, "7th")
