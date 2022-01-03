from django.contrib.auth.views import (
        LoginView,
    )
from django.shortcuts import render
from django.contrib.auth.hashers import get_hasher


class UserLoginView(LoginView):

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        user = self.request.user
        algo, *items = user.password.split('$')
        hasher = get_hasher(algo)
        print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ password items', items)
        return super().get_success_url()



def index(request):
    return render(request, 'profile.html', {})
