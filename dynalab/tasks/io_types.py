import enum


class IOTypeEnum(enum.Enum):
    image_url = "image_url"
    string = "string"
    context_string_selection = "context_string_selection"
    conf = "conf"
    multiple_choice_probs = "multiple_choice_probs"
    multiple_choice = "multiple_choice"
    goal_message_multiple_choice = "goal_message_multiple_choice"

