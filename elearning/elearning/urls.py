from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('chat/', include('chat.urls')),
    path('api/', include('accounts.urls_api')),
    path('', RedirectView.as_view(url='/accounts/home/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
