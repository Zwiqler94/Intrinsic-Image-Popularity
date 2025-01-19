FROM python:3.12.7 AS builder


# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True
# ARG AWS_ACCESS_KEY_ID
# ARG AWS_SECRET_ACCESS_KEY
ENV PIPENV_VENV_IN_PROJECT=1
ENV PIPENV_CACHE_DIR=/home/root/.cache/pipenv

RUN mkdir -pv -m 700 /iipa-workspace
ENV APP_HOME=/iipa-workspace
WORKDIR $APP_HOME 


COPY Pipfile.lock Pipfile ${APP_HOME}/
WORKDIR $APP_HOME


# Install production dependencies.
RUN pip install pipenv
RUN --mount=type=cache,target=/home/root/.cache/pipenv pipenv install


FROM python:3.12.7 AS runtime

RUN pip install pipenv && mkdir -pv -m 700 /iipa-workspace 
ENV APP_HOME=/iipa-workspace
WORKDIR $APP_HOME/


COPY ./ $APP_HOME/


COPY --from=builder /iipa-workspace/.venv/ ${APP_HOME}/.venv/


WORKDIR $APP_HOME/IIPA
ENV GCP_DEV=True
ENV DEBUG=False
ENV LOCAL_DEV=False
ENV IS_BUILDING=True

# RUN --mount=type=secret,id=aws_acc_key,env=AWS_ACCESS_KEY_ID \
#     --mount=type=secret,id=aws_sec_key,env=AWS_SECRET_ACCESS_KEY \
#     IS_BUILDING=True ../.venv/bin/python manage.py makemigrations
     
# RUN --mount=type=secret,id=aws_acc_key,env=AWS_ACCESS_KEY_ID \
#     --mount=type=secret,id=aws_sec_key,env=AWS_SECRET_ACCESS_KEY \
#     IS_BUILDING=True ../.venv/bin/python manage.py migrate

CMD ["../.venv/bin/python", "-m", "gunicorn", "IIPA.asgi:application", "--bind" ,":8000" ,"--log-level", "debug", "--timeout", "100" ,"-k", "uvicorn.workers.UvicornWorker" ,"-c", "gunicorn.conf.py"]

EXPOSE 8000
