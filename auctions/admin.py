from django.contrib import admin
from .models import User,auction,bids,comments,Watchlist

admin.site.register(User)
admin.site.register(auction)
admin.site.register(bids)
admin.site.register(comments)
admin.site.register(Watchlist)
