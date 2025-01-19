# -*- coding: utf-8 -*-

from .rateImage import rateImagesApp, convertDNGtoJPEG
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_http_methods
import os


LOGGER = settings.LOGGER

from .models import ImageRatingForm, ImageRating


# Create your views here.
@require_http_methods(["GET", "POST"])
@xframe_options_exempt
def rate_image(request):
    LOGGER.debug(
        "in rate image" + settings.ENV("AWS_SECRET_ACCESS_KEY")
        if settings.ENV("AWS_SECRET_ACCESS_KEY") is not None
        else "nope"
    )
    if request.method == "POST":
        LOGGER.debug(request.FILES)
        form = ImageRatingForm(request.POST, request.FILES)
        file = form.files["image"]
        fileName, fileExt = os.path.splitext(file.name)
        if fileExt in [".dng", ".DNG"]:
            path = convertDNGtoJPEG(os.path.abspath(file.name))
            with open(path, "r") as neep:
                form.files["images"] = InMemoryUploadedFile(
                    neep, "image", file.name, "image/png", neep.__sizeof__(), None
                )
        LOGGER.debug(form.data)
        LOGGER.debug(form.errors)
        if form.is_valid():
            # form.clean_image()
            i = form.save()
            a = ImageRating.objects.get(uuid=i.uuid)
            LOGGER.debug("A URL: " + i.image.url)
            a.rating_obj = rateImagesApp(
                [i.image.url], os.path.abspath("./model/model-resnet50.pth")
            )
            LOGGER.debug(
                f"Pop Dict: {a.rating_obj} \n {a.rating_obj.get(i.image.url)} "
            )
            a.url = i.image.url
            a.rated_img_name = i.image.name
            a.rated_value = float(a.rating_obj.get(i.image.url))  # type: ignore
            LOGGER.debug("rating: " + str(a.rated_value))
            a.save()
            return HttpResponseRedirect(f"/ratings/{i.uuid}")  # type: ignore
        else:
            return render(request, "imageRater/rater.html", {"form": form}, status=400)
    else:
        form = ImageRatingForm()
        return render(request, "imageRater/rater.html", {"form": form})


@xframe_options_exempt
def post_rate(request, ratingId):
    # resp = HttpResponse(f"thanks, here's your rating: {round(float(rating), 2)} ")
    # resp.status_code = 200
    imageRating = ImageRating.objects.get(uuid=ratingId)
    rating = imageRating.rating_obj.get(imageRating.image.url)
    url = imageRating.image.url
    return render(
        request, "imageRater/post-rate.html", {"rating": round(rating, 2), "url": url}
    )


@require_http_methods(["GET"])
@xframe_options_exempt
def privacy_policy(request):
    return render(request, "imageRater/privacy.html")
