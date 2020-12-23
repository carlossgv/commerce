from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    price = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default="")
    imageURL = models.URLField(blank=True, max_length=500)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator", default="")
    isOpen = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} | {self.creator} | {self.title} | {self.price}"

class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingWatched", default="")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userWatching", default="")

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder", default="")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingBid", default="")
    bid = models.DecimalField(max_digits=11, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.bid}"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commenter", default="")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default="")
    comment = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.commenter} commented: {self.comment}"



