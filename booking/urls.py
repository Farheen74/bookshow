from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', views.home, name='mainpage'), 
    path('detail/<id>', views.movie_detail, name="movie detail"), 
    path('show', views.show_select, name="show select"),
    path('seatselect', views.seat_select, name="seat select"),
    path('bookedseats', views.bookedseats, name="bookedseats"),
    path('checkout', views.checkout, name="checkout"),
    path('booking-confirmed/<int:id>/', views.booking_confirmed, name='booking-confirmed'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('mybookings', views.userbookings, name="user bookings"),
    path('checkout', views.checkout, name="checkout"), 
    path('cancelbooking/<int:id>', views.cancelbooking, name='cancel-booking'), 
]