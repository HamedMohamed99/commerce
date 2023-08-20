from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("CreatListing", views.creat, name="creat"),
    path("listing/<int:id>", views.Listing, name="Listing"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.categories, name="categories2"),
    path("categories/<str:category>/<str:subcategory>", views.categories, name="categories3"),
    path("watchlist", views.watchlist, name="watchlist")
]
