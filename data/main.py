from .control import Control


def main(fullscreen, difficulty, size, audio_device_name_1, audio_device_name_2):
    app = Control(fullscreen, difficulty, size, audio_device_name_1, audio_device_name_2)
    app.run()
