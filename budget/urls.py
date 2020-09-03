from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('home', views.home, name='home'),
    path('logout_user', views.logout_user, name='logout_user'),
    path('signup', views.signup, name='signup'),
    path('user_login', views.user_login, name='user_login'),
    path('add', views.ProjectCreateView.as_view(), name='add'),
    path('<int:project_id>', views.update_status, name='update_status'),
    path('archived_projects', views.archived_projects, name='archived_projects'),
    path('<slug:project_slug>', views.project_detail, name='detail'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
