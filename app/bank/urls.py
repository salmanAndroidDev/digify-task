from django.urls import path
from . import views

urlpatterns = [
    path('open-account/',
         views.OpenAccountAPIView.as_view(),
         name='open_account'),

    path('delete-account/<pk>/',
         views.DeleteAccountAPIView.as_view(),
         name='delete_account'),
]
