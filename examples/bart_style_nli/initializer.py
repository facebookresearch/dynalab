# We are using BART Model, please change tokenizer to the specific model used for example BertModel, RobertaModel etc.

from transformers import BartTokenizer, BartModel

model = BartModel.from_pretrained('facebook/bart-base')
tokenizer = BartTokenizer.from_pretrained('facebook/bart-base')
model.save_pretrained(".")
tokenizer.save_pretrained(".")
