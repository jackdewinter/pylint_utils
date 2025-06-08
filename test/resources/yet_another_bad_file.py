def too_many_arguments(arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8):
    _ = (arg_1, arg_2, arg_3, arg_4, arg_5, arg_6, arg_7, arg_8)


# pylint: disable=too-many-branches
if __name__ == "__main__":
    too_many_arguments(1, 2, 3, 4, 5, 6, 7, 8)
# pylint: enable=too-many-branches
