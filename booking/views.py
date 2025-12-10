from multiprocessing import context
from django.shortcuts import HttpResponseRedirect, render
from django.http import HttpResponse
from django.forms import formset_factory,modelformset_factory
from staff.models import *
from datetime import datetime, date,time,timezone
from django.views.generic.list import ListView
from accounts.views import is_user, user_login_required
from django.contrib.auth.decorators import (user_passes_test)
from .models import *

from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse


def home(request):
    movies = film.objects.filter().values_list('id','movie_name','url', named=True)
    banners = banner.objects.filter().select_related().values_list('movie__id','movie__movie_name','url', named=True)
    return render(request,"index.html", context={'films': movies,'banners':banners})

def movie_detail(request,id):
    context = {}
    context['film'] = film.objects.get(id = id) 
    context ['showtimes'] = show.objects.filter(movie=id,end_date__gte=date.today()).all().values_list('id','showtime',named=True)
    return render(request,"movie_detail.html",context)

@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def show_select(request):
    # Initialize default values
    date = request.GET.get('date', '')
    res_dict = {}
    shows = []
    
    if request.method == "GET" and 'date' in request.GET:
        date = request.GET['date']
        
        # Fetch shows for the selected date
        shows = show.objects.filter(
            end_date__gte=date, 
            start_date__lte=date
        ).select_related(
            'movie_id',
            'movie__url',
            'movie__movie_name'
        ).order_by('movie_id', 'showtime').values_list(
            'id','price','showtime','movie','movie__url','movie__movie_name',
            named=True
        )
        
        # Grouping shows by movie
        for s in shows:
            # legend of fields: showid 0, price 1, showtime 2, movieid 3, movieurl 4, moviename 5
            if s[5] not in res_dict.keys():
                # Movie doesn't exist in dict yet
                res_dict[s[5]] = {
                    'url': s[4],
                    'price': s[1],
                    'showtimes': {s[0]: s[2]},
                    'movieid': s[3]
                }
            else:
                # Movie already exists, add showtime
                res_dict[s[5]]['showtimes'][s[0]] = s[2]
    
    return render(request, "show_selection.html", context={
        'films': res_dict,
        'date': date,
        'shows': shows
    })


@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def seat_select(request):
    """
    Render seat selection page for a specific show
    GET params: show_id, show_date
    """
    context = {}
    show_id = request.GET.get('show_id')
    show_date = request.GET.get('show_date')
    context['show_id'] = show_id
    context['show_date'] = show_date
    # if show id provided, include movie name and showtime for the template
    try:
        if show_id:
            s = show.objects.get(id=show_id)
            context['movie_name'] = s.movie.movie_name
            context['show_time'] = s.showtime.strftime('%I:%M %p') if s.showtime else ''
            # theatre name default
            context['theatre_name'] = 'Main Theatre'
        else:
            context['movie_name'] = ''
            context['show_time'] = ''
            context['theatre_name'] = 'Main Theatre'
    except Exception:
        context['movie_name'] = ''
        context['show_time'] = ''
        context['theatre_name'] = 'Main Theatre'
    return render(request, 'seatselect.html', context)


def bookedseats(request):
    """
    AJAX seat booking info retrival view funciton
    """
    if request.method == 'GET':
           show_id = request.GET['show_id']
           show_date = request.GET['show_date']
           seats = booking.objects.filter(show=show_id,show_date=show_date).values('seat_num')
           booked = ""
           for s in seats:
            booked+=s['seat_num']+","
           return HttpResponse(booked[:-1])
    else:
           return HttpResponse("Request method is not a GET")


def sendEmail(request,message):
    """
    Function to send Email
    """
    template ="Hello "+request.user.username+'\n'+message

    user_email = request.user.email

    email = EmailMessage(
        'Tickets Confirmation Email',
        template,
        settings.EMAIL_HOST_USER,
        [user_email],
    )

    email.fail_silently = False
    email.send()
    return True


@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def checkout(request):
    context = {}
    if (request.method == "POST"):
        show_date_str = request.POST.get('showdate')
        seats = request.POST.get('seats')
        show_id = request.POST.get('showid')
        movie_name = request.POST.get('movie_name') or ''
        theatre_name = request.POST.get('theatre_name') or 'Main Theatre'
        show_time = request.POST.get('show_time') or ''

        # Convert show_date string to date object
        show_date = None
        try:
            from datetime import datetime as dt
            show_date = dt.strptime(show_date_str, '%Y-%m-%d').date() if show_date_str else None
        except Exception as e:
            print(f"Error parsing show_date: {e}")
            show_date = None

        # Get show info where possible
        showinfo = None
        try:
            if show_id:
                showinfo = show.objects.get(id=show_id)
                if not movie_name:
                    movie_name = showinfo.movie.movie_name
                if not show_time and showinfo.showtime:
                    show_time = showinfo.showtime.strftime('%I:%M %p')
        except Exception as e:
            print(f"Error getting show info: {e}")
            showinfo = None

        num_seats = 0
        if seats:
            num_seats = len([s for s in seats.split(',') if s])

        total = 199 * num_seats

        # Create new UserBooking record for ticket UI (primary booking system)
        user_booking = None
        try:
            if show_date and seats:  # Ensure we have required fields
                user_booking = UserBooking.objects.create(
                    user=request.user,
                    movie_name=movie_name,
                    theatre_name=theatre_name,
                    seats=seats,
                    show_date=show_date,
                    show_time=show_time,
                    price=total,
                )
                print(f"UserBooking created: {user_booking.id}")
        except Exception as e:
            print(f"Error creating UserBooking: {e}")
            import traceback
            traceback.print_exc()
            user_booking = None

        # Create old booking model (keeps seat-occupancy behavior)
        try:
            if showinfo is not None and show_date and seats:
                booking.objects.create(
                    user=request.user,
                    show=showinfo,
                    show_date=show_date,
                    booked_date=datetime.now(timezone.utc),
                    seat_num=seats,
                    num_seats=num_seats,
                    total=total,
                )
                print(f"Booking created for show: {showinfo.id}")
        except Exception as e:
            print(f"Error creating booking: {e}")
            import traceback
            traceback.print_exc()

        # If we created a UserBooking, redirect to its confirmation page.
        # Otherwise fall back to the 'my-bookings' page which will show the
        # older `booking`-table entries (if any were created successfully).
        if user_booking:
            return HttpResponseRedirect(reverse('booking-confirmed', args=[user_booking.id]))
        else:
            return HttpResponseRedirect(reverse('my-bookings'))
    # If not POST, redirect back to show selection
    return HttpResponseRedirect('/')

@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def userbookings(request):
    msg=""
    if(request.method == "GET" and len(request.GET)!=0):
        msg = request.GET['ack']

    booking_table = booking.objects.filter(user=request.user).select_related().order_by('-booked_date').values_list('id','show_date','booked_date','show__movie__movie_name','show__movie__url','show__showtime','total','seat_num',named=True)
    
    context = {
        'data':booking_table,
        'msg':msg
    }
    return render(request,"bookings.html",context)


def booking_confirmed(request, id):
    try:
        b = UserBooking.objects.get(id=id, user=request.user)
    except Exception:
        return HttpResponseRedirect('/my-bookings/')
    return render(request, 'booking_confirmed.html', {'booking': b})


@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def my_bookings(request):
    bookings = UserBooking.objects.filter(user=request.user).order_by('-booked_on')
    return render(request, 'my_bookings.html', {'bookings': bookings, 'today': date.today()})

@user_passes_test(user_login_required, login_url='/accounts/usersignin')
def cancelbooking(request,id):
    bobj =  booking.objects.get(id=id)
    message="\nYour tickets are succcessfully Cancelled. Here are the details.\nYour show info{}\nYour Show date {}\nYour seats\n\nThank you,\nBookMyTicket".format(bobj.show,bobj.show_date,bobj.seat_num)
    ack = "Your tickets {} for {} are cancelled successfully".format(bobj.seat_num,bobj.show)
    bobj.delete()
    sendEmail(request,message)
    
    return HttpResponseRedirect("/mybookings?ack="+ack)

