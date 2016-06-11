FROM python:3.5

MAINTAINER "Jakob Rößler <roessler@sighalt.de>"

COPY . /icystream
WORKDIR /icystream
RUN python setup.py install
RUN apt-get -y update
RUN apt-get -y install libav-tools

EXPOSE 8080 5555

CMD ["icystream", "--with-webinterface"]
