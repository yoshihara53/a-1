from django.contrib import admin
from django.urls import path, include

from kadai1.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kadai1.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
