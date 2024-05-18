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


class TranslateTextView(LoginRequiredMixin, View):
    template_name = "translation/translate_text.html"

    def post(self, request, *args, **kwargs):
        if "mode" in request.POST:
            if request.POST.get("mode") == "file-mode":
                return redirect("translation:translate-file")

        input_text = request.POST.get("input_text")
        output_text = TranslationConfig.tlr.translate_text(input_text) if input_text else ""
        return render(
            request,
            self.template_name,
            {"input_text": input_text, "output_text": output_text},
        )

    def get(self, request):
        return render(request, self.template_name)


class TranslateFileView(LoginRequiredMixin, View):
    template_name = "translation/translate_file.html"
    output_dir = Path(settings.MEDIA_ROOT) / "output"

    def post(self, request, *args, **kwargs):
        self.output_dir.mkdir(exist_ok=True)
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
            uploaded_file = str(form.save())
            uploaded_file_path = Path(settings.MEDIA_ROOT) / uploaded_file
            output_file_path = self.output_dir / uploaded_file_path.name
            if uploaded_file_path.suffix == ".pdf":
                TranslationConfig.tlr.translate_pdf(uploaded_file_path, self.output_dir)
            else:
                input_text = uploaded_file_path.read_text()
                output_text = TranslationConfig.tlr.translate_text(input_text)
                output_file_path.write_text(output_text)

            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "uploaded_file": uploaded_file,
                    "output_file": output_file_path.relative_to(settings.MEDIA_ROOT),
                },
            )
        return render(request, self.template_name)

    def get(self, request):
        return render(request, self.template_name)


translate_text_view = TranslateTextView.as_view()
translate_file_view = TranslateFileView.as_view()
