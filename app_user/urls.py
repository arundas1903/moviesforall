from django.conf.urls import url

from .views import User, UserLogin, UpdateUser

urlpatterns = [
    url(r'^$', User.as_view(), name="user_list"),
    url(r'^login_token/$', UserLogin.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', UpdateUser.as_view()),
]
