from dynalab.tasks.io_types import IOTypeEnum


string_mock_data = [
    "It is a good day",
    "Let's try a utf-8 like hackamore from j?\u00a1quima;",
    " ".join([str(x) + "_" for x in range(513)])
]

io_mock_data = {
    IOTypeEnum.image_url.name: [],
    IOTypeEnum.string.name: string_mock_data,
    IOTypeEnum.context_string_selection.name: [],
    IOTypeEnum.conf.name: [],
    IOTypeEnum.multiple_choice_probs.name: [],
    IOTypeEnum.multiple_choice.name: [],
    IOTypeEnum.goal_message_multiple_choice.name: [],
}
