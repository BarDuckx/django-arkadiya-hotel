from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('rooms/', views.RoomListView.as_view(), name='room_list'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/process/', views.process_checkout, name='process_checkout'),

    path('profile/', views.user_profile, name='profile'),
    path('profile/cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),

    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('dashboard/', views.custom_admin_dashboard, name='custom_admin'),
    path('dashboard/category/add/', views.edit_category, name='category_add'),
    path('dashboard/category/<int:pk>/edit/', views.edit_category, name='category_edit'),
    path('dashboard/category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('dashboard/room/add/', views.edit_room, name='room_add'),
    path('dashboard/room/<int:pk>/edit/', views.edit_room, name='room_edit'),
    path('dashboard/room/<int:pk>/delete/', views.room_delete, name='room_delete'),
    path('dashboard/service/add/', views.edit_service, name='service_add'),
    path('dashboard/service/<int:pk>/edit/', views.edit_service, name='service_edit'),
    path('dashboard/service/<int:pk>/delete/', views.service_delete, name='service_delete'),
]
