Sing Pong
=========

Based on https://github.com/metulburr/pong
Tested only on Ubuntu Linux. Should work for macOS, maybe Windows.

## Dependencies:

* PortAudio library (follow install instructions for your OS): http://www.portaudio.com/
* Python 3.5: https://www.python.org/downloads/
* pip (you probably already have this): https://pip.pypa.io/en/stable/installing/


## Installation:

* 'git clone https://github.com:earthfront/sing_pong.git'
* Install portaudio library for your OS.
*  pip install -r requirements.txt


## To run single player:

* 'python ./game.py'
** This should pick up the default input audio device


## To run two players:

* Attach USB microphone.
* Get input device info:
** 'python ./show_input_devices.py'
** Note the indices of two input devices with Max Input Channels > 0. Let's call these numbers X and Y, for each input device index.
* Run 'python ./game.py -1 X -2 Y' where *you replace X and Y with the numbers from the above step*
* X is the right paddle. Y is the left paddle.


## More info and settings:

* Fullscreen: 'python ./game.py -f'
* Help: 'python ./game.py -h'


## It's not working

* Check your audio device settings. Make sure the device is not muted, and is at a normal volume level (for INPUT).
* Reboot. Sometimes the drivers or whatever get borked.
* Check PortAudio troubleshooting: http://www.portaudio.com/
* If the paddle seems out of control, slowly move your pitch up and down and reduce the range of your pitch. The frequency range is small to accommodate most voices.

## Notes

* Tested only on Ubuntu Linux. Should work for macOS, maybe Windows.
