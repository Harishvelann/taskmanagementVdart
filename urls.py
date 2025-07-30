from django.contrib import admin # type: ignore
from django.urls import path, include # type: ignore
from django.shortcuts import redirect # type: ignore
from dashboard import views
from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('create-task/', views.create_task, name='create_task'),
    path('', include('dashboard.urls')),

    # Redirect root URL to login
    path('', lambda request: redirect('login')),

    # Optionally include other dashboard routes (make sure no conflict with above)
    # Remove this if you're already including all necessary views above
    # path('', include('dashboard.urls')), 
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)