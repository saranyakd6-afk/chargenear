from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user:
            return user
        if username and '@' in username and password:
            for u in User.objects.filter(email__iexact=username):
                if u.check_password(password) and self.user_can_authenticate(u):
                    return u
        return None