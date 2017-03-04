#!/usr/bin/env python

import pygame as pg
from data.main import main
import data.tools
import argparse
import sys

parser = argparse.ArgumentParser(description='Pong Arguments')
parser.add_argument(
    '-c',
    '--clean',
    action='store_true',
    help='Remove all .pyc files and __pycache__ directories')

parser.add_argument(
    '-f',
    '--fullscreen',
    action='store_true',
    help='start program with fullscreen')

parser.add_argument(
    '-d',
    '--difficulty',
    default='medium',
    help='where DIFFICULTY is one of the strings [hard, medium, easy], set AI difficulty, default is medium, '
)

parser.add_argument(
    '-s',
    '--size',
    nargs=2,
    default=[1024,768],
    metavar=('WIDTH', 'HEIGHT'),
    help='set window size to WIDTH HEIGHT, defualt is 800 600')

parser.add_argument(
    '-1',
    '--audioinput1',
    nargs=1,
    default=None,
    metavar='int',
    help="Audio input device index 1")

parser.add_argument(
    '-2',
    '--audioinput2',
    nargs=1,
    metavar='int',
    default=None,
    help="Audio input device index 2")

args = vars(parser.parse_args())

if __name__ == '__main__':
    accepted_difficulty = ['hard', 'medium', 'easy']
    size = audio_input_index1 = audio_input_index2 = None

    if args['difficulty']:
        if args['difficulty'].lower() in accepted_difficulty:
            difficulty = args['difficulty'].lower()
            print('difficulty: {}'.format(difficulty))
        else:
            print('{} is not a valid difficulty option, {}'.format(args[
                'difficulty'], accepted_difficulty))
            sys.exit()
            
    if args['size']:
        size = args['size']
        print('window size: {}'.format(size))

    if args["audioinput1"]:
        audio_input_index1 = int(args["audioinput1"][0])
        print('audio input device index 1: ', audio_input_index1)

    if args["audioinput2"]:
        if not audio_input_index1:
            print("Cannot initiate second audio input unless first has been specified.")
            exit(-1)
        audio_input_index2 = int(args["audioinput2"][0])
        print('audio input device index 2: ', audio_input_index2)

    if args['clean']:
        data.tools.clean_files()
    else:
        main(args['fullscreen'], difficulty, size, audio_input_index1, audio_input_index2)
    pg.quit()
