import enum


class AnnotationTypeEnum(enum.Enum):
    image = "image"
    string = "string"
    context_string_selection = "context_string_selection"
    prob = "prob"
    multiclass = "multiclass"
    multilabel = "multilabel"
