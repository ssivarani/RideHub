from django.db import models
from django.contrib.auth.models import User

class Owner(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_picture=models.ImageField(upload_to="owner_profiles/",blank=True,null=True)

    def __str__(self):
        return self.user.username

    def orders_received(self):
        return Booking.objects.filter(
            vehicle__owner=self.user
        ).count()

    orders_received.short_description="Orders Received"

class Renter(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    profile_picture=models.ImageField(
        upload_to="renter_profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username
    def orders_placed(self):
        return Booking.objects.filter(user=self.user).count()
    orders_placed.short_description="Orders Placed"

class Vehicle(models.Model):
    VEHICLE_TYPES=(
        ('Car','Car'),
        ('Bike','Bike'),
        ('Auto','Auto'),
    )
    owner=models.ForeignKey(User,on_delete=models.CASCADE)
    vehicle_type=models.CharField(max_length=20,choices=VEHICLE_TYPES)
    company=models.CharField(max_length=100)
    model=models.CharField(max_length=100)
    number=models.CharField(max_length=20)
    rent=models.IntegerField()
    image=models.ImageField(upload_to='vehicles/')
    available=models.BooleanField(default=True)
    def __str__(self):
        return self.company+" "+self.model

    
class Booking(models.Model):
    STATUS=(
        ('Pending','Pending'),
        ('Approved','Approved'),
        ('Rejected','Rejected'),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    from_date=models.DateField()
    to_date=models.DateField()
    days=models.IntegerField(default=0)
    total_price=models.IntegerField(default=0)
    status=models.CharField(max_length=20,choices=STATUS,default='Pending')
    booked_on=models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, default="Unpaid")
    payment_method = models.CharField(max_length=30, blank=True)
    transaction_id = models.CharField(max_length=50, blank=True)

    def save(self,*args,**kwargs):
        if self.from_date and self.to_date:
            self.days=(self.to_date-self.from_date).days+1
            self.total_price=self.days*self.vehicle.rent
        super().save(*args,**kwargs)

class Review(models.Model):
    booking=models.OneToOneField(Booking,on_delete=models.CASCADE)
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    rating=models.IntegerField()
    comment=models.TextField()
    reviewed_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vehicle.company+" - "+self.user.username
    
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField()
    subject=models.CharField(max_length=200)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

