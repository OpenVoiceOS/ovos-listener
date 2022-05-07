FROM debian:buster-slim

ENV TERM linux
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
  apt-get install -y git python3 python3-dev python3-pip curl build-essential && \
  c_rehash && \
  apt-get autoremove -y && \
  apt-get clean && \
  useradd --no-log-init mycroft -m

# the lines above are kept static so that docker layer is shared and cached among all containers
RUN apt-get install -y portaudio19-dev libpulse-dev swig



COPY . /tmp/ovos-speech
RUN pip3 install /tmp/ovos-speech

# TODO remove this, dependency conflict somewhere....
RUN pip3 install pyee==8.1.0

USER mycroft
ENTRYPOINT mycroft-speech-client