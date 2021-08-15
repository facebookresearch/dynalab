string_mock_data = [
    "It is a good day",
    "Let's try a utf-8 like hackamore from j?\u00a1quima;",
    " ".join([str(x) + "_" for x in range(513)])
]


def get_mock_data(io_type):
    if io_type == "string":
        return string_mock_data
    else:
        return []
