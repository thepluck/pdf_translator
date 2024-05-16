from django.urls import path

from .views import translate_text_view

app_name = "translate_text"
urlpatterns = [
    path("text/", view=translate_text_view, name="translate-text"),
]
