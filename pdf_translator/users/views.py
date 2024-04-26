from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView
from django.shortcuts import render,redirect
from pdf_translator.users.models import User
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.http import HttpResponse

def text_mode(request):
    if request.method == "POST":
        if 'radio' in request.POST:
            mode = request.POST['radio']
            if mode == 'Text':
                return redirect('/users/~text_mode/')
            elif mode == 'file_text':
                return redirect('/users/')
            elif mode == 'file_pdf':
                return redirect('/users/~pdf_mode/')
        return render(request, 'pages/translate_text.html')
    return render(request,'pages/translate_text.html')
def pdf_mode(request):
    if request.method == "POST":
        if 'radio' in request.POST:
            mode = request.POST['radio']
            if mode == 'file_text':
                return redirect('/users/')
            elif mode == 'Text':
                return redirect('/users/~text_mode/')
            elif mode == 'file_pdf':
                return redirect('/users/~pdf_mode/')
        if 'input_file' in request.FILES:
            data = request.FILES['input_file']
            fs = FileSystemStorage()
            filename = fs.save(data.name, data)
            uploaded_file_url = fs.url(filename)
            file_to_send = data
            response = HttpResponse(file_to_send, 'application/x-gzip')
            response['Content-Length'] = file_to_send.size
            response['Content-Disposition'] = f'attachment; filename= {filename}'
            return response

        return render(request,'pages/translate_pdf.html')

    return render(request,'pages/translate_pdf.html')
def get_input_file(request):
    if request.method == "POST":
        if 'radio' in request.POST:
            mode = request.POST['radio']
            if mode == 'file_text':
                return redirect('/users/')
            if mode == 'Text':
                return redirect('/users/~text_mode/')
            if mode == 'file_pdf':
                return redirect('/users/~pdf_mode/')
        if 'input_file' in request.FILES:
            data = request.FILES['input_file']
            fs = FileSystemStorage()
            filename = fs.save(data.name, data)
            uploaded_file_url = fs.url(filename)
            file_to_send = data
            response = HttpResponse(file_to_send, 'application/x-gzip')
            response['Content-Length'] = file_to_send.size
            response['Content-Disposition'] = f'attachment; filename= {filename}'
            return response

        return render(request,"pages/home.html",{'data':'None'})

    else:
        return render(request,"pages/home.html",{'data':'None'})


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self):
        # for mypy to know that the user is authenticated
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self):
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()
