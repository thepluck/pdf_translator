from django.urls import path

from .views import user_detail_view
from .views import user_redirect_view
from .views import user_update_view
from .views import get_input_file
from .views import text_mode,pdf_mode
app_name = "users"
urlpatterns = [
    path('',view=get_input_file,name='get_input'),
    path('~text_mode/', view=text_mode, name='text_mode'),
    path('~pdf_mode/', view=pdf_mode, name='pdf_mode'),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),

]
