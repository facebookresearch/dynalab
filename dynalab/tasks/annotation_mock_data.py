import random

from dynalab.tasks.annotation_types import AnnotationTypeEnum


def get_source_data(annotation, name_to_annotation_dict):
    source_reference_name = annotation["reference_name"]
    source_annotation = name_to_annotation_dict[source_reference_name]
    source_data = annotation_mock_data_generators[source_annotation["type"]](
        source_annotation, name_to_annotation_dict
    )
    return source_data


def generate_image_mock_data(annotation=None, name_to_annotation_dict=None):
    base64_image_string = (
        'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABx0lEQVQ4T2P8'
        + '////fwYKACPVDKhq\nWcHw9etPsFvevPvMICLEy/Dt+y8GBob/DFyc7HAxkDwXJxtDe10kWC3cBQ'
        + 'VVCxkmtMUz/P79h2Hq\n3N0MBRmeDFt3nWf49/8/g6+7EcPUuTsZspPdwZryKxcyTGyPRz'
        + 'UgJmMKg6mhMgMHOyvDnkNXGfS0\nZBmmX3jC8J+RkeFSfzzDqo3H8RsAcwHI2IkzdzCkxDoy'
        + 'WKRNYwAFcaKVKsPJs3cYbC01Gf7+/cdw\n6twdhmWzcrF7AWZAfroHWBMokixMVIn0go'
        + 'EyAxMzE8OBo9cYbC01GB49fsMQ6G0KNiC9aDZDcbYP\ng7aGDPYwQPcCyAVHT95kWLv5FMO7D'
        + '18Y9hleZuA6yMmQYe3CcOosHi8sXLKPYdPSXQwT55YxPH3+\nDuwFYSFehqCGPoYIc0uG6uxA'
        + '3LFgYqDMcGbJRoZslmcMk9XcGJQVxRi8XQ2JCwOYFw4fv8HQN20r\nw+IZ2QxHT95i2LzzLIO'
        + 'KogTD8dO3GBxttBl+/PxNXixMmbOTIT3emYGVlQW7F0BJ+cvXH5Ck/PYL\ng4gwD8P3778YQD'
        + 'kNlHTfvvvCICzEA5bn5mTHTMrkZkiKcyMApgcb4F7rmG8AAAAASUVORK5CYII=\n')
    return [base64_image_string]


def generate_string_mock_data(annotation=None, name_to_annotation_dict=None):
    return [
        "It is a good day",
        "Let's try a utf-8 like hackamore from j?\u00a1quima;",
        " ".join([str(x) + "_" for x in range(513)]),
    ]


def generate_context_string_selection_mock_data(annotation, name_to_annotation_dict):
    source_data = get_source_data(annotation, name_to_annotation_dict)
    return [source_str[0:10] for source_str in source_data]


def generate_conf_mock_data(annotation=None, name_to_annotation_dict=None):
    return [random.random() for _ in range(3)]


def generate_multiclass_probs_mock_data(annotation, name_to_annotation_dict):
    mock_data = []
    source_reference_name = annotation["reference_name"]
    source_annotation = name_to_annotation_dict[source_reference_name]
    labels = source_annotation["labels"]

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


def generate_multiclass_mock_data(annotation, name_to_annotation_dict=None):
    labels = annotation["labels"]
    random.shuffle(labels)
    return labels


def generate_target_label_mock_data(annotation, name_to_annotation_dict=None):
    labels = annotation["labels"]
    random.shuffle(labels)
    return labels


def generate_multilabel_mock_data(annotation, name_to_annotation_dict=None):
    labels = annotation["labels"]
    random.shuffle(labels)
    return [labels]


annotation_mock_data_generators = {
    AnnotationTypeEnum.image.name: generate_image_mock_data,
    AnnotationTypeEnum.string.name: generate_string_mock_data,
    AnnotationTypeEnum.context_string_selection.name: generate_context_string_selection_mock_data,
    AnnotationTypeEnum.conf.name: generate_conf_mock_data,
    AnnotationTypeEnum.multiclass_probs.name: generate_multiclass_probs_mock_data,
    AnnotationTypeEnum.multiclass.name: generate_multiclass_mock_data,
    AnnotationTypeEnum.target_label.name: generate_target_label_mock_data,
    AnnotationTypeEnum.multilabel.name: generate_multilabel_mock_data,
}
