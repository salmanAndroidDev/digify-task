from django.urls import path
from . import views

urlpatterns = [
    path('open-account/',
         views.OpenAccountAPIView.as_view(),
         name='open_account'),

    path('delete-account/<pk>/',
         views.DeleteAccountAPIView.as_view(),
         name='delete_account'),

    path('deposit/<pk>/',
         views.DepositAPIView.as_view(),
         name='deposit'),

    path('withdraw/<pk>/',
         views.WithdrawAPIView.as_view(),
         name='withdraw'),

    path('transfer/<pk>/',
         views.TransferAPIView.as_view(),
         name='transfer'),

    path('create-branch/',
         views.CreateBranchAPIView.as_view(),
         name='create_branch')

]
