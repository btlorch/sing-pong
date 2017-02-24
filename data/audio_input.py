### CODE taken from aubio python demo py_audio.py

# Use pyaudio to open the microphone and run aubio.pitch on the stream of
# incoming samples. If a filename is given as the first argument, it will
# record 5 seconds of audio to this location. Otherwise, the script will
# run until Ctrl+C is pressed.
import typing
from typing import Tuple
import ctypes
import time
import os
import multiprocessing
import functools

import pyaudio
import numpy as np
import aubio
import llist

DEBUG = os.getenv("DEBUG") or False


class PitchDetector():
    def __init__(self, stream):
        self.stream = stream

        # setup pitch
        self.tolerance = 0.8
        self.hop_s = self.buffer_size = self.stream._frames_per_buffer
        self.win_s = self.buffer_size  # 4096  # fft size
        self.pitch_o = aubio.pitch("default", self.win_s, self.hop_s,
                                   self.stream._rate)
        self.pitch_o.set_unit("midi")
        self.pitch_o.set_tolerance(self.tolerance)

    def get_pitch_confidence_tuple(self) -> Tuple[float, float]:
        self.audiobuffer = self.stream.read(
            self.buffer_size, exception_on_overflow=False)
        signal = np.fromstring(self.audiobuffer, dtype=np.float32)

        pitches = self.pitch_o(signal)
        pitch = pitches[0]
        confidence = self.pitch_o.get_confidence()

        if DEBUG:
            print("{} / {}".format(pitch, confidence))

        return (pitch, confidence)

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()


class PitchDetectorFactory():
    def __init__(self):
        # initialise pyaudio
        self.p_audio = pyaudio.PyAudio()
        self.streams = set()

    def get_input_device_infos(self):
        raise NotImplementedError()

    def create_pitch_detector(self, device_index):
        # Get stream info
        stream_info = None
        if not device_index:
            stream_info = self.p_audio.get_default_input_device_info()
        else:
            stream_info = self.p_audio.get_device_info_by_index(device_index)

        # open stream
        self.pyaudio_format = pyaudio.paFloat32
        self.n_channels = 1  # stream_info["maxInputChannels"]
        self.samplerate = stream_info["defaultSampleRate"]
        self.buffer_size = 1024 * 4  # * self.n_channels
        self.device_index = stream_info["index"]

        stream = \
            self.p_audio.open(input_device_index=self.device_index,
                              format=self.pyaudio_format,
                              channels=self.n_channels,
                              rate=44100,
                              input=True,
                              frames_per_buffer=self.buffer_size)
        self.streams.add(stream)
        return PitchDetector(stream)

    def cleanup(self):
        for s in self.streams:
            s.stop_stream()
            s.close()


class MicController():
    def __init__(self,
                 pd_factory,
                 audio_input_index,
                 min_confidence: float=0.8):
        self.min_confidence = min_confidence
        self.pitch_detector = pd_factory.create_pitch_detector(
            audio_input_index)

        # min and max pitches are adjusted by input.
        self.min_pitch = 40.0
        self.max_pitch = 60.0

        self.pitch_cache_list = llist.dllist()
        self.size_limit = 4
        self.range_shrink_speed = 5
        self.range_shrink_interval = 1  # seconds
        self.last_shrink_time = time.clock()

    def shrink_range(self):
        current_time = time.clock()
        if current_time - self.last_shrink_time > 1.0:
            self.min_pitch += self.range_shrink_speed
            self.max_pitch -= self.range_shrink_speed
            self.last_shrink_time = current_time

    def get_normalized_position(self) -> float:
        raw_pitch, confidence = self.pitch_detector.get_pitch_confidence_tuple()
        norm_pitch = 0
        if confidence > self.min_confidence:
            print("p, c: ", raw_pitch, confidence)
            # normalize against a minimum and maximum pitch known in the last "age" seconds, each high and low are saved
            self.min_pitch = min(raw_pitch, self.min_pitch)
            self.max_pitch = max(raw_pitch, self.max_pitch)

            self.pitch_cache_list.appendleft(raw_pitch)
            if self.pitch_cache_list.size >= self.size_limit:
                self.pitch_cache_list.popright()

        if self.pitch_cache_list.size == 0:
            return -1

        avg_raw_pitch = sum(self.pitch_cache_list) / self.pitch_cache_list.size
        norm_pitch = (avg_raw_pitch - self.min_pitch) / (
            self.max_pitch - self.min_pitch)
        return norm_pitch

    def cleanup(self):
        self.run = False
        self.pitch_detector.cleanup()


# Multiprocess
process_running = False
min_confidence = 0.8
child_running = multiprocessing.Value(ctypes.c_bool)
norm_pitch1 = multiprocessing.Value(ctypes.c_double)
norm_pitch2 = multiprocessing.Value(ctypes.c_double)
child_process = None


def process_normalized_positions(child_running, audio_input_index1, audio_input_index2, min_confidence):
    global norm_pitch1
    global norm_pitch2
    # Declare factory
    pd_factory = PitchDetectorFactory()
    mic_controller1 = mic_controller2 = None

    mic_controller1 = MicController(pd_factory, audio_input_index1,
                                    min_confidence)
    if audio_input_index2:
        mic_controller2 = MicController(pd_factory, audio_input_index2,
                                        min_confidence)

    while child_running.value:
        latest_pos = mic_controller1.get_normalized_position()
        norm_pitch1.value = latest_pos

        if audio_input_index2:
            latest_pos = mic_controller2.get_normalized_position()
            norm_pitch2.value = latest_pos

        time.sleep(0.01)

    if mic_controller1:
        mic_controller1.cleanup()

    if mic_controller2:
        mic_controller2.cleanup()

    pd_factory.cleanup()


def get_normalized_position(detector_index=0):
    global norm_pitch1
    global norm_pitch2

    if detector_index == 0:
        return norm_pitch1.value
    else:
        return norm_pitch2.value


def initialize_child_process(audio_input_index1,
                             audio_input_index2,
                             min_confidence_arg=0.8):
    global min_confidence
    global process_running
    global child_process
    global norm_pitches_map
    child_process = multiprocessing.Process(
        target=process_normalized_positions,
        args=(child_running, audio_input_index1,
              audio_input_index2, min_confidence, ))

    min_confidence = min_confidence_arg
    if not child_running.value:
        child_running.value = True
        child_process.start()

    return (0, 1 if audio_input_index2 else None)


def cleanup():
    global process_running
    global child_process
    global child_running
    if child_running.value:
        child_running.value = False
        child_process.join(timeout=3)
        # with child_process.exitcode as ec:
        #     if ec and ec < 0: 
        child_process.terminate()
