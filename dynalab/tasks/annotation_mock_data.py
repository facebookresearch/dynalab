import random

from dynalab.tasks.annotation_types import AnnotationTypeEnum


def get_source_data(annotation, name_to_annotation_dict):
    source_reference_name = annotation["constructor_args"]["reference_name"]
    source_annotation = name_to_annotation_dict[source_reference_name]
    source_data = annotation_mock_data_generators[source_annotation["type"]](
        source_annotation, name_to_annotation_dict
    )
    return source_data


def generate_image_url_mock_data(annotation, name_to_annotation_dict):
    return ["https://dynabench.org/logo_w.png"]


def generate_string_mock_data(annotation, name_to_annotation_dict):
    return [
        "It is a good day",
        "Let's try a utf-8 like hackamore from j?\u00a1quima;",
        " ".join([str(x) + "_" for x in range(513)]),
    ]


def generate_context_string_selection_mock_data(annotation, name_to_annotation_dict):
    source_data = get_source_data(annotation, name_to_annotation_dict)
    return [source_str[0:10] for source_str in source_data]


def generate_conf_mock_data(annotation, name_to_annotation_dict):
    return [random.random() for _ in range(3)]


def generate_multiclass_probs_mock_data(annotation, name_to_annotation_dict):
    mock_data = []
    source_reference_name = annotation["constructor_args"]["reference_name"]
    source_annotation = name_to_annotation_dict[source_reference_name]
    labels = source_annotation["constructor_args"]["labels"]

    for _ in range(3):
        probs_dict = {}
        probs_sum = 0
        for label in labels:
            probs_dict[label] = random.random()
            probs_sum += probs_dict[label]

        # normalize
        for label in labels:
            probs_dict[label] /= probs_sum

        mock_data.append(probs_dict)

    return mock_data


def generate_multiclass_mock_data(annotation, name_to_annotation_dict):
    labels = annotation["constructor_args"]["labels"]
    random.shuffle(labels)
    return labels


def generate_target_label_mock_data(annotation, name_to_annotation_dict):
    labels = annotation["constructor_args"]["labels"]
    random.shuffle(labels)
    return labels


annotation_mock_data_generators = {
    AnnotationTypeEnum.image_url.name: generate_image_url_mock_data,
    AnnotationTypeEnum.string.name: generate_string_mock_data,
    AnnotationTypeEnum.context_string_selection.name: generate_context_string_selection_mock_data,
    AnnotationTypeEnum.conf.name: generate_conf_mock_data,
    AnnotationTypeEnum.multiclass_probs.name: generate_multiclass_probs_mock_data,
    AnnotationTypeEnum.multiclass.name: generate_multiclass_mock_data,
    AnnotationTypeEnum.target_label.name: generate_target_label_mock_data,
}
