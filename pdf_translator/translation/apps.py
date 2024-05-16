from django.apps import AppConfig
from transformers import AutoModelForSeq2SeqLM
from transformers import AutoTokenizer


class TranslationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pdf_translator.translation"
    tokenizer = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi-v2")
    model = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi-v2")
