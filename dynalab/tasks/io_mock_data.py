from dynalab.tasks.io_types import AnnotationTypeEnum


string_mock_data = [
    "It is a good day",
    "Let's try a utf-8 like hackamore from j?\u00a1quima;",
    " ".join([str(x) + "_" for x in range(513)])
]

io_mock_data = {
    AnnotationTypeEnum.image_url.name: [],
    AnnotationTypeEnum.string.name: string_mock_data,
    AnnotationTypeEnum.context_string_selection.name: [],
    AnnotationTypeEnum.conf.name: [],
    AnnotationTypeEnum.multiclass_probs.name: [],
    AnnotationTypeEnum.multiclass.name: [],
    AnnotationTypeEnum.target_label.name: [],
}
