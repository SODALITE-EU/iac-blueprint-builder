FROM python:3.7
ADD . /parser
WORKDIR /parser
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD gunicorn -b 0.0.0.0:80 server:app --timeout 200 --max-requests 10