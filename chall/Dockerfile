from ubuntu:18.04
WORKDIR /CURVE
RUN apt-get update
RUN apt-get install -y curl 
RUN apt-get install -y unzip 
RUN apt-get install -y software-properties-common
RUN apt-get install -y python3.7
RUN curl -L -o infcodechallenge_logprocessor.zip "https://drive.google.com/uc?export=download&id=1IXfcxBreirpED97a2fHwwgw-f70OyulE"
RUN curl -L -o gioCodeCurve.zip "https://drive.google.com/uc?export=download&id=1sLgrIsdvGIwxyNzdQUoTnIfBReY4V6O8"
RUN unzip infcodechallenge_logprocessor.zip
RUN unzip gioCodeCurve.zip
#RUN echo remember to run => python3.7 processInv.py   to start the program
RUN /bin/bash



