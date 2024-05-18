from django import forms

from .models import FileModel


class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = FileModel
        fields = ["file"]
