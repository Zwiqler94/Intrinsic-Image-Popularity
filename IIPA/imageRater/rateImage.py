# -*- coding: utf-8 -*-
from asgiref.sync import async_to_sync
from django.conf import settings
from google.cloud import storage
from io import BytesIO
from PIL import Image
from pydngconverter import DNGConverter, flags
from urllib.request import urlopen
import argparse
import os
import sys
import torch
import torchvision.models
import torchvision.transforms as transforms


LOGGER = settings.LOGGER


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
LOGGER.debug(device.type)
LOGGER.debug(
    f'path: {os.path.join(os.getcwd(), "credential.json")}, creds: {settings.GS_CREDENTIALS}'
)
# LOGGER.debug(f'GCP MODE: {settings.GCP_DEV}, su: {os.environ.get("DJANGO_SUPERUSER_PASSWORD")}, {os.environ.get("DJANGO_SUPERUSER_USERNAME")}')
LOGGER.debug(f"\n\n\nCSRF_ONLY:{settings.CSRF_COOKIE_SECURE} \n\n\n")

popularityDictionary = {}


def prepare_image(image):
    LOGGER.debug("prepare")
    if image.mode != "RGB":
        image = image.convert("RGB")
    Transform = transforms.Compose(
        [
            transforms.Resize([224, 224]),
            transforms.ToTensor(),
        ]
    )
    image = Transform(image)
    image = image.unsqueeze(0)
    LOGGER.debug(image.to(device))
    return image.to(device)


def predict(image, model):
    LOGGER.debug("predict")
    image = prepare_image(image)
    # LOGGER.debug(image)
    with torch.no_grad():
        # LOGGER.debug(model)
        preds = model(image)
        LOGGER.debug(preds.item())
    return round(preds.item(), 4)


def setUpModel():
    model = torchvision.models.resnet50()
    # model.avgpool = nn.AdaptiveAvgPool2d(1) # for any size of the input
    model.fc = torch.nn.Linear(in_features=2048, out_features=1)
    model.load_state_dict(torch.load("model/model-resnet50.pth", map_location=device))
    model.eval().to(device)
    return model


def setArgParser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("-path", dest="path", nargs="+", help="file or folder path")
    parser.add_argument("-e", dest="ext", help="filter extension type")
    args = parser.parse_args()
    return args


def getImagePaths(paths):
    imagePaths = set()
    for root, dirs, files in os.walk(os.path.join(paths)):
        for fileName in files:
            imagePaths.add(os.path.join(root, fileName))
        for dirName in dirs:
            imagePaths.union(getImagePaths(os.path.join(root, dirName)))
    return imagePaths


def rateImages(model, paths):
    paths = getImagePaths(paths[0])
    for path in paths:
        if os.path.isfile(path):
            fileName, fileExtension = os.path.splitext(path)
        if args.ext == fileExtension:  # type: ignore
            image = Image.open(path)
            popularityDictionary[fileName] = predict(image, model)  # type: ignore


def setUpModelApp(modelPath):
    LOGGER.debug(modelPath)
    model = torchvision.models.resnet50()
    # model.avgpool = nn.AdaptiveAvgPool2d(1) # for any size of the input
    model.fc = torch.nn.Linear(in_features=2048, out_features=1)
    model.load_state_dict(torch.load(modelPath, map_location=device))
    model.eval().to(device)
    with open(os.path.join(os.getcwd(), "state_dict.txt"), "w") as neep:
        for tensor in model.state_dict():
            neep.write(f"{tensor}: {model.state_dict()[tensor]}\n")
        neep.close()
    return model


def processImage(popularityDictionary, model, path, processedPath):
    image = Image.open(processedPath)
    popularityDictionary[path] = predict(image, model)
    return image


def getExtensionAndPath(path):
    LOGGER.debug("A path:" + path)
    processedPath = os.path.abspath(os.curdir + "/IIPA/media" + path)
    LOGGER.debug("A.1 processed path" + processedPath)
    fileName = None
    fileExtension = None
    if os.path.isfile(processedPath):
        fileName, fileExtension = os.path.splitext(processedPath)
        LOGGER.debug(fileName, fileExtension)
    return processedPath, fileExtension


def loadModel(modelPath):
    try:
        model = setUpModelApp(os.path.abspath(modelPath))
    except Exception as err:
        LOGGER.debug(sys.exc_info())
        raise err
    LOGGER.debug("post model setup")
    return model


def convertDNGtoJPEG(processedPath):
    pydng = DNGConverter(processedPath, fast_load=True, debug=True)
    path = async_to_sync(pydng.convert_file)(log=LOGGER)
    return path


def processImageGCP(popularityDictionary, model, path):
    LOGGER.debug(path)
    fileName, fileExtension = os.path.splitext(path)
    gStorage = storage.Client(credentials=settings.GS_CREDENTIALS)
    storageObj = gStorage._http.get(path)
    processedPath = storageObj.content
    processedUrl = storageObj.url
    if fileExtension in [".dng", ".DNG"]:
        path = convertDNGtoJPEG(processedUrl)
        image = Image.open(path)
    else:
        image = Image.open(BytesIO(processedPath))
    prediction = predict(image, model)
    LOGGER.debug("prediction: " + str(prediction))
    popularityDictionary[path] = prediction


def processImageLocal(popularityDictionary, model, path):
    processedPath, fileExtension = getExtensionAndPath(path)
    if fileExtension != None:
        image = None
        if fileExtension in [".jpg", ".jpeg", ".png"]:
            image = processImage(popularityDictionary, model, path, processedPath)
        elif fileExtension in [".dng", ".DNG"]:
            path = convertDNGtoJPEG(processedPath)
            image = processImage(popularityDictionary, model, path, processedPath)
        if image != None and settings.DEBUG == True:
            LOGGER.debug(image)
            LOGGER.debug(popularityDictionary)


def rateImagesApp(imagePath, modelPath):
    LOGGER.debug("In rateImagesApp")
    try:
        popularityDictionary = {}
        LOGGER.debug(modelPath)
        model = loadModel(modelPath)
        for path in imagePath:
            if settings.LOCAL_DEV:
                processImageLocal(popularityDictionary, model, path)
            else:
                processImageGCP(popularityDictionary, model, path)
                LOGGER.debug(f"POP POP DICT: {popularityDictionary.__str__()}")
            return popularityDictionary
    except Exception as err:
        LOGGER.debug(sys.exc_info())
        LOGGER.debug(err)
        raise err


if __name__ == "__main__":
    model = setUpModel()
    args = setArgParser()
    rateImages(model, args.path)
    print(dict(sorted(popularityDictionary.items(), key=lambda item: item[1])))
