FROM debian:buster-slim

RUN apt-get update && \
  apt-get install -y git python3 python3-dev python3-pip curl build-essential

# the lines above are kept static so that docker layer is shared and cached among all containers
RUN apt-get install -y portaudio19-dev libpulse-dev swig

COPY . /tmp/ovos-speech
RUN pip3 install /tmp/ovos-speech

ENTRYPOINT mycroft-speech-client