from django.urls import path
from ngo import views

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # HOME
    path('', views.home, name='home'),

    # DONATION
    path('donate/', views.donate, name='donate'),
    path('success/', views.success, name='success'),
    path('donations/', views.donation_list, name='donations'),

    # AUTH
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('volunteer-dashboard/', views.volunteer_dashboard, name='volunteer_dashboard'),

    path('mark-picked/<int:donation_id>/', views.mark_picked, name='mark_picked'),

    path('approve/<int:donation_id>/', views.approve_donation, name='approve'),
path('reject/<int:donation_id>/', views.reject_donation, name='reject'),
path('assign/<int:donation_id>/', views.assign_volunteer, name='assign'),
path('profile/', views.profile, name='profile'),

path('distribute/<int:donation_id>/', views.distribute, name='distribute'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)