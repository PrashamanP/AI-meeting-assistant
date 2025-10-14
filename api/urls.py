from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path("upload/", views.upload_file),
    path("ask/", views.ask_question),
    path("api/kb/<str:kb_id>/files/", views.list_kb_files),
    path("api/kb/<str:kb_id>/summaries/", views.list_kb_summaries),
    path("api/kb/ask/", views.kb_ask_question),
    path("api/login/", views.api_login),
    path("admin/", admin.site.urls),
]
