# from this import d
from django.db import models
from django import forms
from django.contrib.auth.models import AbstractUser
# from traitlets import default
from staff.models import  show
from accounts.models import Account
from datetime import datetime
import uuid


class booking(models.Model):
    booking_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    user = models.ForeignKey(Account,on_delete=models.DO_NOTHING)
    show = models.ForeignKey(show,on_delete=models.CASCADE)
    seat_num = models.CharField(max_length=25)
    num_seats= models.PositiveSmallIntegerField(blank=True, null=True)
    total = models.IntegerField(blank=True, null=True)
    show_date = models.DateField(null=True)
    booked_date = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.booking_code:
            self.booking_code = str(uuid.uuid4().hex[:10]).upper()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return self.seat_num+"@"+self.show_date.strftime("%m/%d/%Y")+" "+self.show.movie.movie_name


class UserBooking(models.Model):
    ticket_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    user = models.ForeignKey('accounts.Account', on_delete=models.CASCADE)
    movie_name = models.CharField(max_length=100)
    theatre_name = models.CharField(max_length=100)
    seats = models.CharField(max_length=200)
    show_date = models.DateField()
    show_time = models.CharField(max_length=50)
    price = models.IntegerField()
    booked_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = str(uuid.uuid4().hex[:10]).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.movie_name} ({self.show_date}) - {self.seats}"
    
