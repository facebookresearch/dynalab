from dynalab.tasks.annotation_types import AnnotationTypeEnum


EPSILON_PREC = 1e-4


def verify_image(obj, name, name_to_config_obj, data):
    assert isinstance(obj, str)


def verify_string(obj, name, name_to_config_obj, data):
    assert isinstance(obj, str)


def verify_context_string_selection(
    obj, name, name_to_config_obj, data
):
    assert isinstance(obj, str)
    assert obj in data[name_to_config_obj[name]["reference_name"]]


def verify_conf(obj, name, name_to_config_obj, data):
    assert isinstance(obj, float)
    assert obj > 0 - EPSILON_PREC
    assert obj < 1 + EPSILON_PREC


def verify_multiclass_probs(obj, name, name_to_config_obj, data):
    assert isinstance(obj, dict)
    assert set(obj.keys()) == set(
        name_to_config_obj[name_to_config_obj[name]["reference_name"]]["labels"]
    )
    assert sum(obj.values()) < 1 + EPSILON_PREC
    assert sum(obj.values()) > 1 - EPSILON_PREC


def verify_multiclass(obj, name, name_to_config_obj, data):
    assert isinstance(obj, str)
    assert obj in name_to_config_obj[name]["labels"]


def verify_target_label(obj, name, name_to_config_obj, data):
    assert isinstance(obj, str)
    assert obj in name_to_config_obj[name]["labels"]


def verify_multilabel(obj, name, name_to_config_obj, data):
    assert isinstance(obj, list)
    for item in obj:
        assert item in name_to_config_obj[name]["labels"]


annotation_verifiers = {
    AnnotationTypeEnum.image.name: verify_image,
    AnnotationTypeEnum.string.name: verify_string,
    AnnotationTypeEnum.context_string_selection.name: verify_context_string_selection,
    AnnotationTypeEnum.conf.name: verify_conf,
    AnnotationTypeEnum.multiclass_probs.name: verify_multiclass_probs,
    AnnotationTypeEnum.multiclass.name: verify_multiclass,
    AnnotationTypeEnum.target_label.name: verify_target_label,
    AnnotationTypeEnum.multilabel.name: verify_multilabel,
}
