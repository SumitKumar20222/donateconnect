from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver



# DONATION MODEL

class Donation(models.Model):

    # Donor
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        related_name='donations'
    )

    # Volunteer
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_donations'
    )

    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=50)
    quantity = models.IntegerField()
    address = models.TextField()

    phone = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Ready', 'Ready for Pickup'),
        ('Picked', 'Picked'),
        ('Distributed', 'Distributed'),
        ('Completed', 'Completed'),
        ('Rejected', 'Rejected'),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    pickup_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    image = models.ImageField(upload_to='donations/', null=True, blank=True)

    def __str__(self):
        return self.name



# PROFILE MODEL

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profiles/', default='profiles/default.png')

    def __str__(self):
        return self.user.username



# AUTO CREATE PROFILE

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



# DISTRIBUTION MODEL

class Distribution(models.Model):
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)

    image = models.ImageField(upload_to='distribution/', null=True, blank=True)

    def __str__(self):
        return f"{self.donation.name} - Distributed"