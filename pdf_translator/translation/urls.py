from django.urls import path

from .views import translate_file_view
from .views import translate_text_view

app_name = "translation"
urlpatterns = [
    path("text/", view=translate_text_view, name="translate-text"),
    path("file/", view=translate_file_view, name="translate-file"),
]
