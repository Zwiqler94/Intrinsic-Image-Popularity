from django.urls import path

from . import views

urlpatterns = [
    path("", views.rate_image, name="rater"),
    path("<str:ratingId>", views.post_rate , name="post-rate")
]