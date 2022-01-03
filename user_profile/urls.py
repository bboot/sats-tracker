from django.urls import path, include

from .views import index, UserLoginView


urlpatterns = [
    path('accounts/login', UserLoginView.as_view(), name="login"),
    path('', index, name="profile"),
]

