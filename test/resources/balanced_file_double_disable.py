"""
This is a test file to check that pylint accepts a double disable and two enables
and that we get that information back in the pylint_utils module.
"""


# pylint: disable=too-many-arguments, too-many-boolean-expressions
def __print_me(first, second, third, fourth, fifth, sixth, seventh):
    if first or second or third or fourth or fifth or sixth or seventh:
        print("At least one argument is provided.")
    print(f"first={first}")
    print(f"second={second}")
    print(f"third={third}")
    print(f"fourth={fourth}")
    print(f"fifth={fifth}")
    print(f"sixth={sixth}")
    print(f"seventh={seventh}")


# pylint: enable=too-many-arguments, too-many-boolean-expressions

__print_me(1, "2", 3.0, 4, "five", 6.00, "7th")
