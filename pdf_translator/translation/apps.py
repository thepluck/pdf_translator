from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from transformers import AutoModelForSeq2SeqLM
from transformers import AutoTokenizer


class TranslationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pdf_translator.translation"
    tokenizer = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi-v2")
    model_path = Path(settings.MODEL_ROOT) / "model"
    if model_path.exists():
        model = AutoModelForSeq2SeqLM.from_pretrained(model_path)
    else:
        model = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi-v2")
        model.save_pretrained(model_path)
