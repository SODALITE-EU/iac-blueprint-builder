FROM python:3.7
ADD . /parser
WORKDIR /parser
RUN pip3 install -r requirements.txt
EXPOSE 80
CMD python main.py

