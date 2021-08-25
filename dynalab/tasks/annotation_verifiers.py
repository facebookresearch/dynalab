from dynalab.tasks.annotation_types import AnnotationTypeEnum


EPSILON_PREC = 1e-4


def verify_image_url(obj, obj_constructor_args, name_to_constructor_args, data):
    assert isinstance(obj, str)


def verify_string(obj, obj_constructor_args, name_to_constructor_args, data):
    assert isinstance(obj, str)


def verify_context_string_selection(
    obj, constructor_args, name_to_constructor_args, data
):
    assert isinstance(obj, str)
    assert obj in data[constructor_args["reference_name"]]


def verify_conf(obj, obj_constructor_args, name_to_constructor_args, data):
    assert isinstance(obj, float)
    assert obj > 0 - EPSILON_PREC
    assert obj < 1 + EPSILON_PREC


def verify_multiclass_probs(obj, obj_constructor_args, name_to_constructor_args, data):
    assert isinstance(obj, dict)
    assert set(obj.keys()) == set(
        name_to_constructor_args[obj_constructor_args["reference_name"]]["labels"]
    )
    assert sum(obj.values()) < 1 + EPSILON_PREC
    assert sum(obj.values()) > 1 - EPSILON_PREC


def verify_multiclass(obj, obj_constructor_args, name_to_constructor_args, data):
    assert isinstance(obj, str)
    assert obj in obj_constructor_args["labels"]


def verify_target_label(obj, obj_constructor_args, name_to_constructor_args, data):
    assert isinstance(obj, str)
    assert obj in obj_constructor_args["labels"]


annotation_verifiers = {
    AnnotationTypeEnum.image_url.name: verify_image_url,
    AnnotationTypeEnum.string.name: verify_string,
    AnnotationTypeEnum.context_string_selection.name: verify_context_string_selection,
    AnnotationTypeEnum.conf.name: verify_conf,
    AnnotationTypeEnum.multiclass_probs.name: verify_multiclass_probs,
    AnnotationTypeEnum.multiclass.name: verify_multiclass,
    AnnotationTypeEnum.target_label.name: verify_target_label,
}
