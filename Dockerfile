FROM python:3.10.2-alpine3.15

ENV MODAK_ENDPOINT "http://modak.sodalite.eu:5000"
ENV MODAK_API_IMAGE "/get_image"
ENV MODAK_API_JOB "/get_job_content"

ADD . /parser
WORKDIR /parser
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD gunicorn -b 0.0.0.0:80 server:app --timeout 200 --max-requests 10