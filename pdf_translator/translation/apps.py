from django.apps import AppConfig

from .utils.translate_pdf import TranslationLayoutRecovery


class TranslationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pdf_translator.translation"
    tlr = TranslationLayoutRecovery()
