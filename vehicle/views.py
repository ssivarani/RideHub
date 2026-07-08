from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Owner,Renter,Vehicle,Booking
from .models import Review
from django.db.models import Sum, Avg
import random, string
from datetime import date
import re

# ---------------- HOME ----------------

def home(request):
    return render(request,"first.html")

# ---------------- LOGIN CHOICE ----------------

def login_choice(request):
    return render(request,"login_choice.html")

#__________aboutus___________________

def about(request):
    return render(request, "aboutus.html")

# ---------------- USER LOGIN ----------------

def user_login(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            if Renter.objects.filter(user=user).exists():
                login(request,user)
                return redirect("user_dashboard")
            else:
                messages.error(request,"Invalid User Account")
                return redirect("user_login")
        else:
            messages.error(request,"Invalid Username or Password")
            return redirect("user_login")
    return render(request,"user_login.html")

# ---------------- OWNER LOGIN ----------------

def owner_login(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user=authenticate(request,username=username,password=password)
        if user is not None:
            if Owner.objects.filter(user=user).exists():
                login(request,user)
                return redirect("owner_dashboard")
            else:
                messages.error(request,"Invalid Owner Account")
                return redirect("owner_login")
        else:
            messages.error(request,"Invalid Username or Password")
            return redirect("owner_login")
    return render(request,"owner_login.html")

# ---------------- ADMIN LOGIN ----------------

def admin_login(request):
    logout(request)
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    return redirect("/admin/")

# -------- contact -----------
from .models import Contact

def contact(request):
    if request.method=="POST":
        Contact.objects.create(
            name=request.POST["name"],
            email=request.POST["email"],
            subject=request.POST["subject"],
            message=request.POST["message"]
        )
        return render(request,"contact.html",{"success":True})
    return render(request,"contact.html")

# ---------------- SIGNUP ----------------
def signup(request):
    if request.method == "POST":
        if request.POST["captcha"].upper() != request.session.get("captcha", ""):
            messages.error(request, "Invalid CAPTCHA")
            return redirect("signup")

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]
        role = request.POST["role"]

        if len(password) < 8:
           messages.error(request, "Password must be at least 8 characters long.")
           return redirect("signup")

        if not re.search(r"[A-Za-z]", password):
            messages.error(request, "Password must contain at least one letter.")
            return redirect("signup")

        if not re.search(r"\d", password):
            messages.error(request, "Password must contain at least one number.")
            return redirect("signup")
  
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("signup")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("signup")
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password

        )
        if role == "owner":
            Owner.objects.create(user=user)
        else:
            Renter.objects.create(user=user)
        messages.success(request, "Registration Successful. Please Login.")
        return redirect("signup")

    captcha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    request.session["captcha"] = captcha
    return render(request, "signup.html", {"captcha": captcha})

# ---------------- USER DASHBOARD ----------------

@login_required
def user_dashboard(request):
    renter = Renter.objects.get(user=request.user)
    total_bookings=Booking.objects.filter(user=request.user).count()
    pending_bookings=Booking.objects.filter(user=request.user,status="Pending").count()
    approved_bookings=Booking.objects.filter(user=request.user,status="Approved").count()
    featured_vehicles=Vehicle.objects.filter(available=True).order_by("-id")[:3]
    return render(request,"user_dashboard.html",{
        "renter": renter,
        "total_bookings":total_bookings,
        "pending_bookings":pending_bookings,
        "approved_bookings":approved_bookings,
        "featured_vehicles":featured_vehicles
    })

# ---------------- OWNER DASHBOARD ----------------

@login_required
def owner_dashboard(request):
    owner = Owner.objects.get(user=request.user)
    vehicles=Vehicle.objects.filter(owner=request.user)
    approved_bookings=Booking.objects.filter(
        vehicle__owner=request.user,
        status="Approved",
        payment_status="Paid"

    )
    pending_bookings=Booking.objects.filter(
        vehicle__owner=request.user,
        status="Pending"
    )
    recent_bookings=Booking.objects.filter(
        vehicle__owner=request.user
    ).order_by("-booked_on")[:5]

    recent_vehicles=vehicles.order_by("-id")[:4]
    total_earnings=approved_bookings.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    return render(request,"owner_dashboard.html",{
        "owner": owner,
        "total_vehicles":vehicles.count(),
        "total_bookings":approved_bookings.count(),
        "pending_requests":pending_bookings.count(),
        "total_earnings":total_earnings,
        "recent_bookings":recent_bookings,
        "recent_vehicles":recent_vehicles
    })

# ---------------- ADD VEHICLE ----------------

@login_required
def add_vehicle(request):
    owner = Owner.objects.get(user=request.user)
    if request.method=="POST":
        Vehicle.objects.create(
            owner=request.user,
            vehicle_type=request.POST["vehicle_type"],
            company=request.POST["company"],
            model=request.POST["model"],
            number=request.POST["number"],
            rent=request.POST["rent"],
            image=request.FILES["image"]
        )
        messages.success(request,"Vehicle added successfully.")
        return redirect("my_vehicles")
    return render(request, "add_vehicle.html", {
        "owner": owner
    })

# ---------------- MY VEHICLES ----------------

from datetime import date
@login_required
def my_vehicles(request):

    today = date.today()
    vehicles = Vehicle.objects.filter(
        owner=request.user
    ).order_by("-id")

    for vehicle in vehicles:
        vehicle.is_booked = Booking.objects.filter(
            vehicle=vehicle,
            status="Approved",
            from_date__lte=today,
            to_date__gte=today
        ).exists()
    return render(request,"my_vehicles.html",{
        "vehicles":vehicles
    })

# ---------------- VEHICLE DETAILS ----------------

@login_required
def vehicle_details(request,vid):

    vehicle=Vehicle.objects.get(id=vid)
    reviews=Review.objects.filter(vehicle=vehicle).order_by("-reviewed_on")
    average_rating=reviews.aggregate(
        Avg("rating")
    )["rating__avg"]

    approved_bookings=Booking.objects.filter(
        vehicle=vehicle,
        status="Approved"
    )
    total_bookings=approved_bookings.count()
    total_earnings=approved_bookings.aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0

    return render(request,"vehicle_details.html",{
        "vehicle":vehicle,
        "reviews":reviews,
        "average_rating":average_rating,
        "total_bookings":total_bookings,
        "total_earnings":total_earnings
    })
# ---------------- EDIT VEHICLE ----------------

@login_required
def edit_vehicle(request,vid):
    vehicle=Vehicle.objects.get(
        id=vid,
        owner=request.user
    )
    if request.method=="POST":
        vehicle.vehicle_type=request.POST["vehicle_type"]
        vehicle.company=request.POST["company"]
        vehicle.model=request.POST["model"]
        vehicle.number=request.POST["number"]
        vehicle.rent=request.POST["rent"]

        if "image" in request.FILES:
            vehicle.image=request.FILES["image"]
        vehicle.save()

        messages.success(request,"Vehicle updated successfully.")
        return redirect("vehicle_details",vid=vehicle.id)
    return render(request,"edit_vehicle.html",{
        "vehicle":vehicle
    })

# ---------------- DELETE VEHICLE ----------------

@login_required
def delete_vehicle(request,vid):
    vehicle=Vehicle.objects.get(
        id=vid,
        owner=request.user
    )
    if request.method=="POST":
        vehicle.delete()
        messages.success(request,"Vehicle deleted successfully.")
        return redirect("my_vehicles")
    return render(request,"delete_vehicle.html",{
        "vehicle":vehicle
    })

# ---------------- ALL VEHICLES ----------------

from datetime import date
@login_required
def all_vehicles(request):
    renter = Renter.objects.get(user=request.user)
    today = date.today()
    vehicles = Vehicle.objects.all()
    search = request.GET.get("search")
    vehicle_type = request.GET.get("type")
    max_rent = request.GET.get("rent")

    if search:
        vehicles = vehicles.filter(company__icontains=search) | vehicles.filter(model__icontains=search)
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    if max_rent:
        vehicles = vehicles.filter(rent__lte=max_rent)

    vehicles = vehicles.order_by("-id")

    for vehicle in vehicles:
        vehicle.is_booked = Booking.objects.filter(
            vehicle=vehicle,
            status="Approved",
            from_date__lte=today,
            to_date__gte=today
        ).exists()
    return render(request, "all_vehicles.html", {
        "renter": renter,
        "vehicles": vehicles
    })

# ---------------- BOOK VEHICLE ----------------

@login_required
def book_vehicle(request,vid):
    renter = Renter.objects.get(user=request.user)
    vehicle=Vehicle.objects.get(id=vid)
    if request.method=="POST":
        from datetime import datetime
        from_date=datetime.strptime(request.POST["from_date"],"%Y-%m-%d").date()
        to_date=datetime.strptime(request.POST["to_date"],"%Y-%m-%d").date()

        if from_date < date.today():
            messages.error(request, "You cannot book a vehicle for a past date.")
            return redirect("book_vehicle", vid=vid)

        if from_date>to_date:
            messages.error(request,"To Date must be after From Date.")
            return redirect("book_vehicle",vid=vid)

        overlap=Booking.objects.filter(
            vehicle=vehicle,
            status="Approved"
        ).filter(
            from_date__lte=to_date,
            to_date__gte=from_date
        ).exists()
        if overlap:
            messages.error(
                request,
                "Vehicle is already booked for the selected dates."
            )

            return redirect("book_vehicle",vid=vid)
        booking=Booking.objects.create(
            user=request.user,
            vehicle=vehicle,
            from_date=from_date,
            to_date=to_date,
            status="Pending",
            payment_status="Unpaid"
        )
        return redirect("payment",bid=booking.id)
    return render(request,"book_vehicle.html",{"vehicle":vehicle,
                                               "renter": renter

    })

# ---------------- OWNER BOOKINGS ----------------

@login_required
def owner_bookings(request):
    owner = Owner.objects.get(user=request.user)
    bookings=Booking.objects.filter(
        vehicle__owner=request.user
    ).order_by("-booked_on")
    return render(request,"owner_bookings.html",{
        "owner": owner,
        "bookings":bookings
    })

# ---------------- APPROVE BOOKING ----------------

@login_required
def approve_booking(request,bid):
    booking=Booking.objects.get(id=bid)
    booking.status="Approved"
    booking.save()
    messages.success(request,"Booking Approved.")
    return redirect("owner_bookings")

# ---------------- REJECT BOOKING ----------------

@login_required
def reject_booking(request,bid):
    booking=Booking.objects.get(id=bid)
    booking.status="Rejected"
    booking.save()
    messages.error(request,"Booking Rejected.")
    return redirect("owner_bookings")

# ---------------- CANCEL BOOKING ----------------

@login_required
def cancel_booking(request,bid):
    booking=Booking.objects.get(
        id=bid,
        user=request.user
    )
    booking.status="Rejected"
    booking.save()
    messages.success(request,"Booking Cancelled.")
    return redirect("my_bookings")

# ---------------- MY BOOKINGS ----------------

from .models import Booking, Review
@login_required
def my_bookings(request):
    renter = Renter.objects.get(user=request.user)
    selected_status = request.GET.get("status", "all")
    bookings = Booking.objects.filter(
        user=request.user,
        payment_status="Paid"
    )
    if selected_status != "all":
        bookings = bookings.filter(status=selected_status)
    bookings = bookings.order_by("-booked_on")
    reviewed_ids = list(
        Review.objects.filter(user=request.user)
        .values_list("booking_id", flat=True)
    )
    return render(request, "my_bookings.html", {
        "renter": renter,
        "bookings": bookings,
        "selected_status": selected_status,
        "reviewed_ids": reviewed_ids,
    })

# ---------------- LOGOUT ----------------

def logout_user(request):
    logout(request)
    messages.success(
        request,
        "Logged out successfully."
    )
    return redirect("home")

#-------------USER_PROFILE--------------

@login_required
def user_profile(request):
    renter=Renter.objects.get(user=request.user)
    total_bookings=Booking.objects.filter(user=request.user).count()
    approved=Booking.objects.filter(
        user=request.user,
        status="Approved"
    ).count()
    pending=Booking.objects.filter(
        user=request.user,
        status="Pending"
    ).count()
    return render(request,"user_profile.html",{
        "renter":renter,
        "total_bookings":total_bookings,
        "approved":approved,
        "pending":pending
    })

#----------OWNER_PROFILE------------

@login_required
def owner_profile(request):
    owner=Owner.objects.get(user=request.user)
    total_vehicles=Vehicle.objects.filter(owner=request.user).count()
    approved_bookings=Booking.objects.filter(
        vehicle__owner=request.user,
        status="Approved"
    ).count()
    pending_requests=Booking.objects.filter(
        vehicle__owner=request.user,
        status="Pending"
    ).count()
    total_earnings=Booking.objects.filter(
        vehicle__owner=request.user,
        status="Approved",
        payment_status="Paid"
    ).aggregate(
        Sum("total_price")
    )["total_price__sum"] or 0
    return render(request,"owner_profile.html",{
        "owner":owner,
        "total_vehicles":total_vehicles,
        "approved_bookings":approved_bookings,
        "pending_requests":pending_requests,
        "total_earnings":total_earnings
    })

@login_required
def add_review(request, bid):
    booking = Booking.objects.get(
        id=bid,
        user=request.user,
        status="Approved"
    )
    review = Review.objects.filter(booking=booking).first()
    if request.method == "POST":
        if review:
            review.rating = request.POST["rating"]
            review.comment = request.POST["comment"]
            review.save()
            messages.success(request, "Review updated successfully.")
        else:
            Review.objects.create(
                booking=booking,
                vehicle=booking.vehicle,
                user=request.user,
                rating=request.POST["rating"],
                comment=request.POST["comment"]
            )
            messages.success(request, "Review added successfully.")

        return redirect("my_bookings")
    return render(request, "add_review.html", {
        "booking": booking,
        "review": review,
    })

@login_required
def booking_receipt(request,bid):
    booking=Booking.objects.get(id=bid,user=request.user)
    return render(request,"booking_receipt.html",{
        "booking":booking
    })

@login_required
def edit_profile(request):
    if request.method=="POST":
        username=request.POST["username"]
        email=request.POST["email"]
        if User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request,"Username already exists")
            return redirect("edit_profile")
        request.user.username=username
        request.user.email=email
        request.user.save()
        if Owner.objects.filter(user=request.user).exists():
            owner=Owner.objects.get(user=request.user)
            if "profile_picture" in request.FILES:
                owner.profile_picture=request.FILES["profile_picture"]
                owner.save()
            messages.success(request,"Profile updated successfully")
            return redirect("owner_profile")

        if Renter.objects.filter(user=request.user).exists():
            renter=Renter.objects.get(user=request.user)
            if "profile_picture" in request.FILES:
                renter.profile_picture=request.FILES["profile_picture"]
                renter.save()
            messages.success(request,"Profile updated successfully")
            return redirect("user_profile")
    if Owner.objects.filter(user=request.user).exists():
        owner=Owner.objects.get(user=request.user)
        return render(request,"owner_edit_profile.html",{
            "owner":owner
        })
    renter=Renter.objects.get(user=request.user)
    return render(request,"user_edit_profile.html",{
        "renter":renter
    })


@login_required
def logout_user(request):
    logout(request)
    return redirect("home")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404
from django.db.models import Sum,Avg

@login_required
def vehicle(request, vid):
    vehicle = get_object_or_404(Vehicle, id=vid)
    return render(request, "vehicle.html", {
        "vehicle": vehicle,
    })

@login_required
def payment(request, bid):
    booking = Booking.objects.get(
        id=bid,
        user=request.user
    )
    if request.method == "POST":
        booking.payment_status = "Paid"
        booking.payment_method = request.POST["method"]
        booking.transaction_id = "RH" + str(random.randint(100000,999999))
        booking.save()
        messages.success(request,"Payment Successful")
        return redirect("my_bookings")
    return render(request,"payment.html",{
        "booking":booking
    })