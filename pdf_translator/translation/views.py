from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from tasks import translate_text


class TranslateTextView(LoginRequiredMixin, APIView):
    def post(self, request):
        text = request.data.get("text")
        if not text:
            return Response({"error": "text is required"}, status=400)

        translated_text = translate_text.delay(text)
        return Response(
            {"output": translated_text},
            template_name="translation/translate_text.html",
        )

    def get(self, request):
        return Response(template_name="translation/translate_text.html")


translate_text_view = TranslateTextView.as_view()
