from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.db.models import Q
from django.urls import reverse



from .models import *



def index(request):
    all_active_listing = auction.objects.exclude(Active=False).all().order_by('-time')
    return render(request, "auctions/index.html", {
                "all_active_listing": all_active_listing
            })


def categories(request, category=None, subcategory=None):
    if not category and not subcategory:
        all_active_listing = auction.objects.exclude(Active=False).all().order_by('-time')
        return render(request, "auctions/categories.html", {
                    "all_active_listing": all_active_listing,
                    "categories": categories_dic()
                })
    
    elif category and not subcategory:
        all_active_listing = auction.objects.filter(Q(listing_category=category) & Q(Active=True)).all().order_by('-time')
        return render(request, "auctions/categories.html", {
                    "all_active_listing": all_active_listing,
                    "category": category,
                    "subcategories": categories_dic()[category] if category != 'other' else None
                })
    
    else:
        all_active_listing = auction.objects.filter(Q(listing_category=category) & Q(sub_category=subcategory) & Q(Active=True)).all().order_by('-time')
        return render(request, "auctions/categories.html", {
                    "all_active_listing": all_active_listing,
                    "category": category,
                    "subcategory": subcategory
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
    

@login_required
def watchlist(request):
    watchlist = auction.objects.filter(id__in=Watchlist.objects.filter(user=request.user).values_list('item', flat=True)).all().order_by('-time')
    return render(request, "auctions/watchlist.html", {
                "watchlist": watchlist
            })

    

@login_required
def creat(request):
    if request.method == "POST":
        new = auction()
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["bid"]
        image = request.POST["image"]

        if title == "" and description == "" and starting_bid == "" :
            return render(request, "auctions/creat.html", {
                "message": "must provide Title, description and Stating bid."
            })
        
        new.title = title
        new.description = description
        new.starting_bid = starting_bid
        new.current_bid = starting_bid
        
        if image != "" :
            new.image = image

        if request.POST["categorySelect"] != "":
            new.listing_category = request.POST["categorySelect"]

        if request.POST["subcategorySelect"] != "":
            new.sub_category = request.POST["subcategorySelect"]

        new.user = request.user
        new.save()

        return redirect(reverse('index'))

    return render(request, "auctions/creat.html", {
            "categories": categories_dic()
        })

def categories_dic():
    categories = {
    "Motors": ["Cars & Trucks", "Motorcycles & Powersports", "Boats & Marine", "RVs & Campers", "Parts & Accessories"],
    "Electronics": ["Computers & Tablets", "Smartphones & Cell Phones", "TVs & Home Theater", "Cameras & Photo", "Musical Instruments", "Video Games & Consoles"],
    "Collectibles & Art": ["Antiques & Collectibles", "Coins & Paper Money", "Jewelry & Watches", "Stamps", "Trading Cards"],
    "Home & Garden": ["Yard, Garden & Outdoor Living", "Tools & Workshop Equipment", "Home Improvement", "Kitchen, Dining & Bar Supplies", "Home Decor"],
    "Clothing, Shoes & Accessories": ["Men's Clothing", "Women's Clothing", "Children's Clothing", "Shoes & Sneakers", "Handbags & Accessories"],
    "Toys & Hobbies": ["Toys & Games", "Collectibles", "Sports Memorabilia", "Dolls & Bears", "Trading Cards"],
    "Sporting Goods": ["Sports Equipment", "Clothing & Footwear", "Toys & Games", "Collectibles", "Fan Shop"],
    "Books, Movies & Music": ["Books", "Movies & TV", "Music", "Video Games"],
    "Health & Beauty": ["Beauty & Personal Care", "Health & Wellness", "Medical Equipment", "Fitness & Sports Nutrition"],
    "Business & Industrial": ["Industrial Equipment", "Tools & Supplies", "Commercial & Retail Equipment", "Business Services"],
    "Pet Supplies": ["Pet Food & Supplies", "Pet Toys & Accessories", "Pet Clothing & Grooming", "Veterinary Supplies"],
    "Baby Essentials": ["Baby Clothing & Accessories", "Baby Gear & Furniture", "Toys & Games", "Diapers & Wipes"]
    }
    return categories


def current_bids(id):
    try:
        current_bid = bids.objects.get(Q(auction=id) & Q(Active=True)).bid
        bid_exists = True
    except bids.DoesNotExist:
        current_bid = auction.objects.get(pk=id).starting_bid
        bid_exists = False

    return current_bid, bid_exists


# Function to close a listing by updating its Active status and redirecting to the listing page
def creator_close_listing(id):
    auction_instance = auction.objects.get(pk=id)
    auction_instance.Active = False
    auction_instance.save()
    return redirect(reverse('Listing', args=[id]))

# Function to handle user bidding on an auction
def user_bidding(current_bid, request, id , bid_exits):
    if not request.POST["bid"] :
        return "you must provide a bid."

    if float(request.POST["bid"]) <= current_bid and bid_exits:
        return f"Your bid must be more than {current_bid}."

    elif float(request.POST["bid"]) < current_bid and not bid_exits:
        return f"Your bid must be {current_bid} or higher."
    
    else:
        bids.objects.filter(auction=id).update(Active=False)
        new = bids()
        new.auction = auction.objects.get(pk=id)
        new.user = request.user 
        new.bid = request.POST["bid"]
        new.save()
        auction.objects.filter(pk=id).update(current_bid = new.bid)
        return redirect(reverse('Listing', args=[id]))

# Function to add or remove an item from the user's watchlist
def add_or_remove_watchlist(request, id):
    if Watchlist.objects.filter(Q(user=request.user) & Q(item=id)):
        if request.method == "POST" and 'form1_submit' in request.POST:
            Watchlist.objects.get(Q(item=id) & Q(user=request.user )).delete()
            return redirect(reverse('Listing', args=[id]))
        return "Remove From Watchlist", True
    else:
        if request.method == "POST" and 'form1_submit' in request.POST:
            new = Watchlist()
            new.item = auction.objects.get(pk=id)
            new.user = request.user 
            new.save()
            return redirect(reverse('Listing', args=[id]))
        return "Add to Watchlist", True

# Function to add a comment to an auction
def add_comment(request, id):
    new = comments()
    new.user = request.user 
    new.auction = auction.objects.get(pk=id)
    new.comment = request.POST["comment"]
    new.save()
    return redirect(reverse('Listing', args=[id]))

# Main view function to display an auction listing
def Listing(request, id):
    message = ""
    current_bid, bid_exits = current_bids(id)
    is_creator = auction.objects.get(pk=id).user == request.user

    if auction.objects.get(pk=id).Active:

        if request.user.is_authenticated:
            if request.method == "POST" and 'form3_submit' in request.POST:
                if request.POST["comment"] :
                    return add_comment(request, id)
                else :
                    message = "comment is Empty"

            if is_creator:
                if request.method == "POST" and 'form1_submit' in request.POST:
                    return creator_close_listing(id)

                top_button = "close"
                bid = False

            else:
                if request.method == "POST" and 'form2_submit' in request.POST:
                    message = user_bidding(current_bid, request, id , bid_exits)
                    if isinstance(message, HttpResponseRedirect):
                        return message

                result = add_or_remove_watchlist(request, id)
                if isinstance(result, HttpResponseRedirect):
                    return result
                else:
                    top_button, bid = result

            return render(request, "auctions/Listing.html", {
                "message": message,
                "id": id,
                "listing": auction.objects.get(pk=id),
                "comments": comments.objects.filter(auction=id),
                "top_button": top_button,
                "bid": bid
            })

        return render(request, "auctions/Listing.html", {
            "listing": auction.objects.get(pk=id),
            "comments": comments.objects.filter(auction=id)
        })

    else:
        return render(request, "auctions/Listing.html", {
            "id": id,
            "message": f"- This Listing closed and the winner is {bids.objects.get(Q(auction=id) & Q(Active=True)).user.username} -",
            "listing": auction.objects.get(pk=id),
            "comments": comments.objects.filter(auction=id),
            "frez": True
        })