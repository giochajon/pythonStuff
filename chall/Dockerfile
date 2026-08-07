from ubuntu:18.04
WORKDIR /CURVE
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    software-properties-common \
    python3.7 \
    && rm -rf /var/lib/apt/lists/*
RUN curl -L -o infcodechallenge_logprocessor.zip "https://drive.google.com/uc?export=download&id=1IXfcxBreirpED97a2fHwwgw-f70OyulE"
RUN curl -L -o gioCodeCurve.zip "https://drive.google.com/uc?export=download&id=1sLgrIsdvGIwxyNzdQUoTnIfBReY4V6O8"
RUN unzip infcodechallenge_logprocessor.zip
RUN unzip gioCodeCurve.zip
#RUN echo remember to run => python3.7 processInv.py   to start the program

RUN useradd --create-home --shell /bin/bash challuser && chown -R challuser /CURVE
USER challuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python3.7 -c "exit(0)" || exit 1

CMD ["/bin/bash"]



