from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category, Watchlist


def index(request):

    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })

def watchlist(request):
    if Watchlist.objects.filter(user = request.user).exists():
        listings = Watchlist.objects.filter(user = request.user)
        message = ""
    else:
        message = "You are not watching any listing!"
        listings = []


    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "message": message,
        "watchlist": watchlist
    })

def listing(request, title):
    listing = Listing.objects.get(title=title)
    price = listing.price
    isOpen = listing.isOpen
    watchlistMessage = ""
    bidMessage = ""
    closedMessage = ""
    comments = Comment.objects.filter(listing=listing)
    watchlistButton = ""

    if request.user.is_authenticated:
        user = request.user
    

    if listing.isOpen == False:
        print('im here')
        if Bid.objects.filter(listing=listing).exists():
            winner = Bid.objects.filter(listing=listing).order_by('-bid').first().bidder
            closedMessage = f'Listing closed, winner: {winner}'
        else:
            closedMessage = f'Listing closed by creator'



    if request.POST:
        if 'addWatchlist' in request.POST:
            comment = Watchlist(listing = listing, user = user)
            if Watchlist.objects.filter(listing = listing, user = user).exists():
                watchlistMessage = "Already on watchlist!"
                watchlistButton = False
            else:
                comment.save()
                watchlistButton = True
        elif 'removeWatchlist' in request.POST and Watchlist.objects.filter(listing = listing, user = user).exists():
            Watchlist.objects.filter(listing = listing, user = user).delete()

        if 'makeBid' in request.POST:
            bid = int(request.POST.get('bidAmmount'))
            if bid <= listing.price:
                bidMessage = f"Bid has to be greater than {listing.price}"
            else:
                Listing.objects.filter(title=title).update(price=bid)
                price = bid
                bidCreated = Bid(bidder = user, listing = listing, bid = bid)
                bidCreated.save()
                bidMessage = "Bid placed!"

        if 'submitComment' in request.POST:
            comment = request.POST.get("newComment")
            if comment == "":
                pass
            else:
                newComment = Comment(listing=listing, commenter=user, comment=comment)
                newComment.save()

        if 'closeButton' in request.POST:
            Listing.objects.filter(title=title).update(isOpen = False)
            isOpen = False
            if Bid.objects.filter(listing=listing).exists():
                winner = Bid.objects.filter(listing=listing).order_by('-bid').first().bidder
                closedMessage = f'Listing closed, winner: {winner}'
            else:
                closedMessage = f'Listing closed by creator'

    if request.user.is_authenticated:
        if Watchlist.objects.filter(listing = listing, user = user).exists():
            watchlistButton = False
        else:
            watchlistButton = True
            
    return render(request, "auctions/listing.html", {
        "title": listing.title,
        "description": listing.description,
        "price": price,
        "category": listing.category,
        "imageURL": listing.imageURL,
        "creator": listing.creator,
        "comments": comments,
        "watchlistMessage": watchlistMessage,
        "bidMessage": bidMessage,
        "isOpen": isOpen,
        "closedMessage": closedMessage,
        "watchlistButton": watchlistButton
    })    


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    categories = Category.objects.all()

    if request.method == "POST":
        
        title = request.POST["title"]
        description = request.POST["description"]
        startingBid = request.POST["startingBid"]
        category = request.POST["category"]

        category = Category.objects.get(name=category)

        imageURL = request.POST["imageURL"]
        newListing = Listing(title=title, description=description, price=startingBid, category=category,imageURL=imageURL,creator=request.user)
        newListing.save()

        return HttpResponseRedirect(f"listing/{title}")

    
    return render(request, "auctions/create.html", {
        "categories": categories
    })



def categories(request):
    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category):
    categoryKey = Category.objects.get(name=category).id
    listings = Listing.objects.filter(category=categoryKey)
    print(listings)

    return render(request, f"auctions/category.html", {
        "category": category,
        "listings": listings
    })