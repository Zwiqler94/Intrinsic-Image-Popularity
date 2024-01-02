# -*- coding: utf-8 -*-
from fileinput import filename
from .rateImage import rateImagesApp, convertDNGtoJPEG
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt
from PIL import Image
import os
from pydngconverter import DNGConverter, flags

import logging

logger = logging.getLogger(__file__)


from .models import ImageRatingForm, ImageRating


# Create your views here.
@xframe_options_exempt
def rate_image(request):
    logger.debug("in rate image" + settings.ENV("AWS_SECRET_KEY"))
    if request.method == "POST":
        logger.debug(request.FILES)
        form = ImageRatingForm(request.POST, request.FILES)
        file = form.files["image"]
        fileName, fileExt = os.path.splitext(file.name)
        if fileExt in [".dng", ".DNG"]:
            path = convertDNGtoJPEG(os.path.abspath(file.name))
            with open(path, "r") as neep:
                form.files["images"] = InMemoryUploadedFile(
                    neep, "image", file.name, "image/png", neep.__sizeof__(), None
                )
        logger.debug(form.data)
        logger.debug(form.errors)
        if form.is_valid():
            # form.clean_image()
            i = form.save()
            a = ImageRating.objects.get(uuid=i.uuid)
            logger.debug("A URL: " + i.image.url)
            a.rating_obj = rateImagesApp(
                [i.image.url], os.path.abspath("./model/model-resnet50.pth")
            )
            a.url = i.image.url
            a.rated_img_name = i.image.name
            a.rated_value = float(a.rating_obj.get(i.image.url)) # type: ignore
            logger.debug("rating: " + str(a.rated_value))
            a.save()
            return HttpResponseRedirect(f"/{i.uuid}")  # type: ignore
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
