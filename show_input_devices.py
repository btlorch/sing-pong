#!/usr/bin/env python

import pyaudio

p = pyaudio.PyAudio()
device_infos = [
    p.get_device_info_by_index(i) for i in range(0, p.get_device_count())
]

enumerated_device_names = list(
    enumerate([(i['name'], i['maxInputChannels']) for i in device_infos]))

for e in enumerated_device_names:
    print("Device Index: {}, Name: {}, Max Input channels: {}".format(e[0], e[1][0], e[1][1]))
