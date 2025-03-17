from django.urls import path
# from . import views
from .views import UserLoginView, UserRegisterView, UserRedirectView, UserLogoutView, UserPasswordResetView, UserPasswordResetDoneView, UserPasswordResetConfirmView, UserPasswordResetCompleteView, UserPasswordChangeView, UserPasswordChangeDoneView
urlpatterns = [
    path('login/', UserLoginView.as_view(), name = 'login'),
    path('register/', UserRegisterView.as_view(), name = 'register'),
    path('redirect/', UserRedirectView.as_view(), name = 'redirect'),
    path('logout/', UserLogoutView.as_view(), name = 'logout'),
    path('pass_reset/', UserPasswordResetView.as_view(), name = 'pass_reset'),
    path('pass_reset_done/', UserPasswordResetDoneView.as_view(), name = 'pass_reset_done'),   
    path('pass_reset_confirm/<uidb64>/<token>', UserPasswordResetConfirmView.as_view(), name = 'pass_reset_confirm'),
    path('pass_reset_complete/', UserPasswordResetCompleteView.as_view(), name = 'pass_reset_complete'),  
    path('pass_change/', UserPasswordChangeView.as_view(), name = 'pass_change'),
    path('pass_change_done/', UserPasswordChangeDoneView.as_view(), name = 'pass_change_done'), 
]