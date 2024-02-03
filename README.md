# Intrinsic image popularity Assessment

A fork of [Intrinsic image popularity Assessment](https://github.com/dingkeyan93/Intrinsic-Image-Popularity)

This is a PyTorch implementation of the paper [Intrinsic Image Popularity Assessment](https://arxiv.org/abs/1907.01985).

## CLI Script
Run `python src/rateImage.py -path <path-to-directory> -e <image-ext>` to evaluate the intrinsic image popularity of your photos on Instagram.

## TO Run

Follow the cloudbuild.yaml file

### Env Vars:

- `export SERVICE_URL_TAGS=$(gcloud run services describe iipa  --format "value(status.traffic.tag)")`
- `export SERVICE_URL=$(gcloud run services describe iipa  --format "value(status.url)")`
- `export SERVICE_ACCOUNT=$(gcloud run services describe iipa  --format "value(spec.template.spec.serviceAccountName)")`
- `export DJANGO_SUPERUSER_PASSWORD=$(gcloud secrets versions access latest --secret=superuser_password)`

1. `gcloud builds submit --config cloudbuild.yaml --substitutions _SERVICE_URL_TAGS=$SERVICE_URL_TAGS,_CLOUDRUN_SERVICE_URL=$SERVICE_URL,TAG_NAME=v0.10.5`
2. `gcloud run deploy iipa --image gcr.io/iipa-32fdd/iipa:latest --service-account $SERVICE_ACCOUNT --set-env-vars DEBUG=False,GCP_DEV=True,SERVICE_URL_TAGS=$SERVICE_URL_TAGS,CLOUDRUN_SERVICE_URL=$SERVICE_URL` 
3. make sure Firebase Hosting is rewriting reqs correctly
