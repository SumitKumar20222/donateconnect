from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Donation



# Create your views here.
from django.shortcuts import render



def home(request):
    return render(request, 'ngo/home.html')


from .models import Donation


@login_required
def donate(request):
    if request.method == "POST":

        name = request.POST.get('name')
        item_type = request.POST.get('item_type')
        quantity = request.POST.get('quantity')
        address = request.POST.get('address')
        pickup_date = request.POST.get('pickup_date')

        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        print("LAT:", latitude, "LNG:", longitude)  

        image = request.FILES.get('image')

        Donation.objects.create(
            user=request.user,
            name=name,
            item_type=item_type,
            quantity=quantity,
            address=address,
            pickup_date=pickup_date,
            latitude=latitude,     
            longitude=longitude,   
            image=image,
            phone=phone,
            email=email
        )

        return redirect('success')

    return render(request, 'ngo/donate.html')

def success(request):
    return render(request, 'ngo/success.html')
from django.contrib.auth.decorators import login_required

@login_required
def donation_list(request):

    if request.user.is_staff:
        donations = Donation.objects.all()   # admin
    else:
        donations = Donation.objects.filter(user=request.user)  # user

    return render(request, 'ngo/donation_list.html', {
        'donations': donations
    })

from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from django.contrib.auth import login

def register(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'ngo/register.html', {'error': 'Passwords do not match'})

        user = User.objects.create_user(username=username, email=email, password=password)

        login(request, user)  # auto login

        return redirect('/donate/')  # donate page

    return render(request, 'ngo/register.html')

from django.contrib.auth import authenticate, login
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            #  ROLE BASED REDIRECT
            if user.is_staff:
                return redirect('/admin-dashboard/')   # admin

            elif Donation.objects.filter(assigned_to=user).exists():
                return redirect('/volunteer-dashboard/')  #volunteer

            else:
                return redirect('/dashboard/')  # normal user

        else:
            return render(request, 'ngo/login.html', {'error': 'Invalid credentials'})

    return render(request, 'ngo/login.html')

from django.contrib.auth import logout
from django.shortcuts import redirect

def user_logout(request):
    logout(request)
    return redirect('/')   # home page

@login_required
def dashboard(request):
    donations = Donation.objects.filter(user=request.user)

    return render(request, 'ngo/dashboard.html', {
        'donations': donations
    })

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    donations = Donation.objects.all()

    return render(request, 'ngo/admin_dashboard.html', {
        'donations': donations
    })

from django.contrib.auth.decorators import login_required

@login_required
def volunteer_dashboard(request):
    donations = Donation.objects.filter(
        assigned_to=request.user
    )

    return render(request, 'ngo/volunteer_dashboard.html', {
        'donations': donations
    })


from django.shortcuts import get_object_or_404

@login_required
def mark_picked(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)

    # security: only assigned volunteer can mark as picked
    if donation.assigned_to == request.user:
        donation.status = "Picked"
        donation.save()

    return redirect('volunteer_dashboard')


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('/')

    donations = Donation.objects.all()
    users = User.objects.all()   

    return render(request, 'ngo/admin_dashboard.html', {
        'donations': donations,
        'users': users
    })


from django.shortcuts import get_object_or_404

@login_required
def approve_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    donation.status = "Ready"
    donation.save()
    return redirect('admin_dashboard')


@login_required
def reject_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    donation.status = "Rejected"
    donation.save()
    return redirect('admin_dashboard')

@login_required
def assign_volunteer(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)

    if request.method == "POST":
        user_id = request.POST.get('user_id')
        donation.assigned_to = User.objects.get(id=user_id)
        donation.save()

    return redirect('admin_dashboard')


from .models import Profile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def profile(request):

    profile, created = Profile.objects.get_or_create(user=request.user)

    donations = Donation.objects.filter(user=request.user)

    total_items = sum(d.quantity for d in donations)

    if request.method == "POST":
        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')
            profile.save()

    return render(request, 'ngo/profile.html', {
        'profile': profile,
        'donations': donations,
        'total_items': total_items
    })

from .models import Distribution, Donation
from django.shortcuts import get_object_or_404

@login_required
def distribute(request, donation_id):

    donation = get_object_or_404(Donation, id=donation_id)

    if request.method == "POST":

        location = request.POST.get('location')
        notes = request.POST.get('notes')
        image = request.FILES.get('image')

        Distribution.objects.create(
            donation=donation,
            location=location,
            notes=notes,
            image=image
        )

        # STATUS UPDATE
        donation.status = "Distributed"
        donation.save()

        return redirect('volunteer_dashboard')

    return render(request, 'ngo/distribute.html', {'donation': donation})



from supabase import create_client
from django.conf import settings

def donate(request):

    supabase = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )

    if request.method == "POST":
        file = request.FILES.get("image")

        image_url = None

        if file:
            file_path = f"donations/{file.name}"

            supabase.storage.from_("media").upload(file_path, file.read())

            image_url = supabase.storage.from_("media").get_public_url(file_path)



def donate(request):
    if request.method == "POST":
        file = request.FILES.get("image")

        image_url = None

        if file:
            file_path = f"donations/{file.name}"

            supabase.storage.from_("media").upload(file_path, file.read())

            image_url = supabase.storage.from_("media").get_public_url(file_path)

        Donation.objects.create(
            user=request.user,
            name=request.POST.get("name"),
            item_type=request.POST.get("item_type"),
            quantity=request.POST.get("quantity"),
            address=request.POST.get("address"),
            image=image_url
        )

        return redirect('success')
    
   