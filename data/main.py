from .control import Control

def main(fullscreen, difficulty, size, audio_input_index1, audio_input_index2):
    app = Control(fullscreen, difficulty, size, audio_input_index1, audio_input_index2)
    app.run()
