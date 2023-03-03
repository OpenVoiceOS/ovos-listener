from ovos_listener.arecord import ArecordStream
import webrtcvad


class Frame:
    """Represents a "frame" of audio data."""

    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(audio, sample_rate=16000, agressiveness=1):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    vad = webrtcvad.Vad(agressiveness)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)

    total = len(frames)
    detections = 0
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            detections += 1
    if detections >= total / 2:
        return True
    return False


sample_rate = 16000

agressiveness = 2  # 1, 2 or 3

counter = 0
thresh = 2  # consecutive "is_speaking" detections to change state
thresh2 = 25  # consecutive "not_speaking" detections to change state

audio_stream = ArecordStream(sample_rate=sample_rate)
audio_stream.start()

speaking = False
prev_detection = False
try:
    while True:
        frame = audio_stream.read()

        if not frame:
            continue

        detection = vad_collector(frame, sample_rate, agressiveness)

        if detection != prev_detection:
            counter += 1
        else:
            counter = 0

        if detection and counter >= thresh and not speaking:
            print("Speech started")
            speaking = True
            counter = 0
            prev_detection = detection
        elif not detection and counter >= thresh2 and speaking:
            print("Speak finished")
            speaking = False
            counter = 0
            prev_detection = detection

except KeyboardInterrupt:
    print("Terminating")
    audio_stream.stop()
