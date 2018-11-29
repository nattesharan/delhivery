FROM python:3.5
ADD . /delhivery
WORKDIR /delhivery
RUN pip install -r requirements.txt
RUN pip install gunicorn
EXPOSE 8080
