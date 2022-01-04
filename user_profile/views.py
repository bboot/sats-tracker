from django.contrib.auth.views import (
        LoginView,
    )
from django.shortcuts import render
from django.contrib.auth.hashers import get_hasher, Argon2PasswordHasher


class MyArgon2PasswordHasher(Argon2PasswordHasher):
    def verify(self, password, encoded):
        argon2 = self._load_library()
        hasher = argon2.PasswordHasher()
        return super().verify(password, encoded)



class UserLoginView(LoginView):

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        '''
        Going to use the raw password + a salt to generate the
        key for decrypting the database entries.
        NB: If this were a multi-user app, then use js and end-to-end
        encryption, as that is the only legitimate (read: trustless)
        way to protect the user's private data.

        TAKE 2: Not a good idea, just use the key stored on the
        server. If you want to use the user's key for encryption,
        then do end-to-end.
        '''
        user = self.request.user
        algo, *items = user.password.split('$')
        hasher = get_hasher(algo)
        assert algo == 'argon2', 'Was expecting Argon2 password hasher.'
        return super().get_success_url()



def index(request):
    return render(request, 'profile.html', {})
