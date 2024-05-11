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
from .model_vinai import translate_en2vi
from .model_vietAi import translate_vietai
from PyPDF2 import PdfReader
# from googletrans import Translator
# translator = Translator()
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
        data = request.POST['textinput']
        model = request.POST['radio-model']
        data_tran = ''
        if model == 'vin':
            data_tran = translate_en2vi(data)
            # data_tran = ''
        elif model == 'viet':
            # data_tran = ''
            data_tran = translate_vietai(data)
        elif model == 'gg':
            # data_tran =  translator.translate(data,src='en',dest='vi')
            # data_tran = data_tran.text

            data_tran = data_tran + ' (by google translate)'
        return render(request, 'pages/translate_text.html',{"output": data_tran})
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

            text = ''
            model = request.POST['radio-model']
            if model == 'vin':
                file = open(f'pdf_translator/media/{filename}', 'rb')
                renderr = PdfReader(file)
                number_of_pages = len(renderr.pages)
                for page in range(number_of_pages):
                    p = renderr.pages[page]
                    text += translate_en2vi(p.extract_text()) + '\n'
            elif model == 'viet':
                file = open(f'pdf_translator/media/{filename}', 'rb')
                renderr = PdfReader(file)
                number_of_pages = len(renderr.pages)
                for page in range(number_of_pages):
                    p = renderr.pages[page]
                    text += translate_vietai(p.extract_text()) + '\n'
            # elif model == 'gg':
            #     file = open(f'pdf_translator/media/{filename}', 'rb')
            #     renderr = PdfReader(file)
            #     number_of_pages = len(renderr.pages)
            #     for page in range(number_of_pages):
            #         p = renderr.pages[page]
            #         # trans = translator.translate(p.extract_text(),src='en',dest='vi')
            #         # text += trans.text + '\n'
            # d ịch file

            response = HttpResponse(text, 'application/x-gzip')
            response['Content-Disposition'] = f'attachment; filename= output.doc'
            # trả cho người dùng file đã dịch
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
            text_tran = ''
            model = request.POST['radio-model']
            if model == 'vin':
                with open(f'pdf_translator/media/{filename}', 'r+') as inp:
                    text = inp.readline()
                    while text:
                        text_tran += translate_en2vi(text) + '\n'
                        text = inp.readline()
            elif model == 'viet':
                with open(f'pdf_translator/media/{filename}', 'r+') as inp:
                    text = inp.readline()
                    while text:
                        text_tran += translate_vietai(text) + '\n'
                        text = inp.readline()
            # elif model == 'gg':
            #     with open(f'pdf_translator/media/{filename}', 'r+') as inp:
            #         text = inp.readline()
            #         while text:
            #             trans = translator.translate(text,src='en',dest='vi')
            #             text_tran += trans.text + '\n'
            #             text = inp.readline()

            # text_trans = translate_en2vi(text) #d ịch file
            response = HttpResponse(text_tran, 'application/x-gzip')
            response['Content-Disposition'] = f'attachment; filename= {model}.txt'
            # trả cho người dùng file đã dịch
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
