from dynalab.tasks.io_types import IOTypeEnum


def verify_image_url(obj, obj_constructor_args, name_to_constructor_args, example_io):
    assert isinstance(obj, str)


def verify_string(obj, obj_constructor_args, name_to_constructor_args, example_io):
    assert isinstance(obj, str)


def verify_context_string_selection(
    obj, constructor_args, name_to_constructor_args, example_io
):
    assert isinstance(obj, str)
    assert obj in example_io[constructor_args["reference_key"]]


def verify_conf(obj, obj_constructor_args, name_to_constructor_args, example_io):
    assert isinstance(obj, float)
    assert obj > -0.001
    assert obj < 1.001


def verify_multiple_choice_probs(
    obj, obj_constructor_args, name_to_constructor_args, example_io
):
    assert isinstance(obj, dict)
    assert set(obj.keys()) == set(
        name_to_constructor_args[obj_constructor_args["reference_key"]]["labels"]
    )
    assert sum(obj.values()) < 1.001
    assert sum(obj.values()) > 0.999


def verify_multiple_choice(
    obj, obj_constructor_args, name_to_constructor_args, example_io
):
    assert isinstance(obj, str)
    assert obj in obj_constructor_args["labels"]


def verify_goal_message_multiple_choice(
    obj, obj_constructor_args, name_to_constructor_args, example_io
):
    assert isinstance(obj, str)
    assert obj in obj_constructor_args["labels"]


io_type_verifiers = {
    IOTypeEnum.image_url.name: verify_image_url,
    IOTypeEnum.string.name: verify_string,
    IOTypeEnum.context_string_selection.name: verify_context_string_selection,
    IOTypeEnum.conf.name: verify_conf,
    IOTypeEnum.multiple_choice_probs.name: verify_multiple_choice_probs,
    IOTypeEnum.multiple_choice.name: verify_multiple_choice,
    IOTypeEnum.goal_message_multiple_choice.name: verify_goal_message_multiple_choice,
}
