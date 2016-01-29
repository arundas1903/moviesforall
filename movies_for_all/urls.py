from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic.base import TemplateView

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='help.html')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^user/', include('app_user.urls')),
    url(r'^movies/', include('movies.urls')),
    url(r'^api/', include('rest_framework.urls', namespace='rest_framework'))
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'static/(?P<path>.*)',
         'serve',
         {'document_root': settings.STATIC_ROOT}), )


urlpatterns += patterns('',
                        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
                            {'document_root': settings.STATIC_ROOT}),)