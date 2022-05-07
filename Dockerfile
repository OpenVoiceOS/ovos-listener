FROM openvoiceos/core:dev

RUN apt-get install -y portaudio19-dev libpulse-dev swig

COPY . /tmp/ovos-speech
RUN pip3 install /tmp/ovos-speech

USER mycroft

ENTRYPOINT mycroft-speech-client