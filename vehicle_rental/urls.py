"""
URL configuration for vehicle_rental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from vehicle import views

urlpatterns=[
    path('admin/',admin.site.urls),
    path('',views.home,name='home'),
    path('signup/',views.signup,name='signup'),
    path('login-choice/',views.login_choice,name='login_choice'),
    path('user-login/',views.user_login,name='user_login'),
    path('owner-login/',views.owner_login,name='owner_login'),
    path('user-dashboard/',views.user_dashboard,name='user_dashboard'),
    path('owner-dashboard/',views.owner_dashboard,name='owner_dashboard'),
    path('admin-login/',views.admin_login,name='admin_login'),
    path('add-vehicle/',views.add_vehicle,name='add_vehicle'),
    path('my-vehicles/',views.my_vehicles,name='my_vehicles'),
    path("vehicle-details/<int:vid>/", views.vehicle_details, name="vehicle_details"),
    path('approve/<int:bid>/',views.approve_booking,name='approve_booking'),
path('reject/<int:bid>/',views.reject_booking,name='reject_booking'),
path('owner-bookings/',views.owner_bookings,name='owner_bookings'),
path('cancel-booking/<int:bid>/',views.cancel_booking,name='cancel_booking'),
path('my-bookings/',views.my_bookings,name='my_bookings'),
path('edit-vehicle/<int:vid>/',views.edit_vehicle,name='edit_vehicle'),
path('delete-vehicle/<int:vid>/',views.delete_vehicle,name='delete_vehicle'),
path('vehicles/',views.all_vehicles,name='all_vehicles'),
path('book/<int:vid>/',views.book_vehicle,name='book_vehicle'),
path('logout/',views.logout_user,name='logout'),
path('user-profile/',views.user_profile,name='user_profile'),
path('owner-profile/',views.owner_profile,name='owner_profile'),
path('add-review/<int:bid>/',views.add_review,name='add_review'),
path('booking-receipt/<int:bid>/',views.booking_receipt,name='booking_receipt'),
path('edit-profile/',views.edit_profile,name='edit_profile'),
path('logout/',views.logout_user,name='logout'),
path('login/', views.login_choice, name='login_choice'),
path("vehicle/<int:vid>/", views.vehicle, name="vehicle"),
path("payment/<int:bid>/",views.payment,name="payment"),
path("contact/",views.contact,name="contact"),
path("about/", views.about, name="about"),
path(
    "cancel-payment/<int:bid>/",
    views.cancel_payment,
    name="cancel_payment"
),
]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

