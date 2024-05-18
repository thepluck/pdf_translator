from django.db import models


class UploadedFile(models.Model):
    file = models.FileField(upload_to="uploads/")
    file_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Uploaded File"
        verbose_name_plural = "Uploaded Files"

    def __str__(self):
        return self.file.name
