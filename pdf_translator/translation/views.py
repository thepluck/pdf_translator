import logging
from pathlib import Path

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views import View

from .apps import TranslationConfig
from .forms import UploadedFileForm

logger = logging.getLogger(__name__)


def translate_text(en_text: str) -> str:
    tokenizer = TranslationConfig.tokenizer
    model = TranslationConfig.model
    input_ids = tokenizer(en_text, return_tensors="pt").input_ids
    output_ids = model.generate(
        input_ids,
        decoder_start_token_id=tokenizer.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True,
    )
    vi_text = tokenizer.batch_decode(output_ids, skip_special_tokens=True)
    return " ".join(vi_text)


class TranslateTextView(LoginRequiredMixin, View):
    template_name = "translation/translate_text.html"

    def post(self, request, *args, **kwargs):
        if "mode" in request.POST:
            if request.POST.get("mode") == "file-mode":
                return redirect("translation:translate-file")

        input_text = request.POST.get("input_text")
        output_text = translate_text(input_text) if input_text else ""
        return render(
            request,
            self.template_name,
            {"input_text": input_text, "output_text": output_text},
        )

    def get(self, request):
        return render(request, self.template_name)


class TranslateFileView(LoginRequiredMixin, View):
    template_name = "translation/translate_file.html"

    def post(self, request, *args, **kwargs):
        if "mode" in request.POST:
            if request.POST.get("mode") == "text-mode":
                return redirect("translation:translate-text")
        if "download_path" in request.POST:
            download_path = request.POST.get("download_path")
            file_path = Path(settings.MEDIA_ROOT) / download_path
            file_name = file_path.name
            with Path.open(file_path, "rb") as f:
                response = HttpResponse(
                    f.read(),
                    content_type="application/force-download",
                )
            response["Content-Disposition"] = f"attachment; filename={file_name}"
            return response
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save()
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "uploaded_file": uploaded_file,
                },
            )
        return render(request, self.template_name)

    def get(self, request):
        return render(request, self.template_name)


translate_text_view = TranslateTextView.as_view()
translate_file_view = TranslateFileView.as_view()
