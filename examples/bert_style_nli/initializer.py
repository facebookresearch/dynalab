# We are using Bert Model, please change tokenizer to the specific model used for example BartModel, RobertaModel etc.

from transformers import BertTokenizer, BertConfig, BertModel

# bert-base-uncased: the name of the chosen model found in HuggingFace
model = BertModel.from_pretrained('bert-base-uncased')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model.save_pretrained(".")
tokenizer.save_pretrained(".")
