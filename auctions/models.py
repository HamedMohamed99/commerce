from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    def __str__(self):
        return f"{self.id} {self.username}"

class auction(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_auction")
    description = models.TextField()
    starting_bid = models.FloatField()
    current_bid = models.FloatField()
    image = models.TextField(null=True, blank=True)
    listing_category = models.CharField(max_length=100, blank=True)
    sub_category = models.CharField(max_length=100, blank=True)
    Active = models.BooleanField(default=True)
    time = models.DateTimeField(default=timezone.now)

class bids(models.Model):
    id = models.BigAutoField(primary_key=True)
    auction = models.ForeignKey(auction, on_delete=models.CASCADE, related_name="auction_bids")
    bid = models.FloatField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    Active = models.BooleanField(default=True)
    time = models.DateTimeField(default=timezone.now)

class comments(models.Model):
    id = models.BigAutoField(primary_key=True)
    auction = models.ForeignKey(auction, on_delete=models.CASCADE, related_name="auction_comments")
    comment = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    time = models.DateTimeField(default=timezone.now)


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_Watchlist")
    item = models.ForeignKey(auction, on_delete=models.CASCADE, related_name="item")
    