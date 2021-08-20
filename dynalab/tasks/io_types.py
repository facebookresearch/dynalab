import enum


class AnnotationTypeEnum(enum.Enum):
    image_url = "image_url"
    string = "string"
    context_string_selection = "context_string_selection"
    conf = "conf"
    multiclass_probs = "multiclass_probs"
    multiclass = "multiclass"
    target_label = "target_label"

