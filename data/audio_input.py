from pygame._sdl2 import (
    get_audio_device_names,
    AudioDevice,
    AUDIO_F32,
    AUDIO_ALLOW_FORMAT_CHANGE,
)
from typing import Tuple
import multiprocessing
import ctypes
import numpy as np
import aubio
import llist
import time


class PitchDetector(object):
    """
    Estimate the pitch/fundamental frequency of an audio signal
    """
    def __init__(self, hop_size, sample_rate, pitch_tolerance=0.8):
        # The hop size is the number of samples in between successive frames.
        # The hop size should be smaller than the frame size, so that frames overlap.
        self.pitch_o = aubio.pitch(method="yinfft", buf_size=4096, hop_size=hop_size, samplerate=sample_rate)
        self.pitch_o.set_unit("midi")
        self.pitch_o.set_tolerance(pitch_tolerance)

    def get_pitch_confidence_tuple(self, signal) -> Tuple[float, float]:
        pitches = self.pitch_o(signal)
        pitch = pitches[0]
        confidence = self.pitch_o.get_confidence()

        # print("{} / {}".format(pitch, confidence))

        return pitch, confidence


class MicController(object):
    def __init__(self, device_name, sample_rate, buffer_size, pitch_tolerance, min_confidence):
        self.device_name = device_name
        self.min_confidence = min_confidence

        self.pitch_detector = PitchDetector(buffer_size, sample_rate, pitch_tolerance)
        self.pitch = multiprocessing.Value(ctypes.c_double)
        self.confidence = multiprocessing.Value(ctypes.c_double)

        # min and max pitches are adjusted by input.
        self.min_pitch = 40.0
        self.max_pitch = 60.0

        self.pitch_cache_list = llist.dllist()
        self.cache_size_limit = 5

        def callback(audio_device, audio_memory_view):
            sound_chunk = bytes(audio_memory_view)
            signal = np.frombuffer(sound_chunk, dtype=np.float32)

            pitch, confidence = self.pitch_detector.get_pitch_confidence_tuple(signal)
            self.pitch.value = pitch
            self.confidence.value = confidence

        # Set up audio device
        self.audio_device = AudioDevice(
            devicename=device_name,
            iscapture=True,
            frequency=sample_rate,
            audioformat=AUDIO_F32,
            numchannels=1,
            chunksize=buffer_size,
            allowed_changes=AUDIO_ALLOW_FORMAT_CHANGE,
            callback=callback,
        )

        # Pause playback
        self.audio_device.pause(0)

    def get_normalized_position(self) -> float:
        raw_pitch = self.pitch.value
        raw_confidence = self.confidence.value

        if raw_pitch < self.min_pitch * 0.8:
            # Too small, ignore
            print("Pitch too low")
            pass

        elif raw_pitch > self.max_pitch * 1.2:
            # Too high, ignore
            print("Pitch too high")
            pass

        elif raw_confidence < self.min_confidence:
            print("Low confidence")
            pass

        else:
            self.pitch_cache_list.appendleft(raw_pitch)
            if self.pitch_cache_list.size >= self.cache_size_limit:
                self.pitch_cache_list.popright()

        if self.pitch_cache_list.size == 0:
            return -1

        avg_raw_pitch = sum(self.pitch_cache_list) / self.pitch_cache_list.size
        norm_pitch = (avg_raw_pitch - self.min_pitch) / (self.max_pitch - self.min_pitch)

        print(f"Raw pitch: {raw_pitch}, normalized mean pitch: {norm_pitch}")
        norm_pitch = np.clip(norm_pitch, 0, 1)

        return norm_pitch
