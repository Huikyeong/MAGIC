import tobii_research as tr
import time
import math
from win32api import GetSystemMetrics
from pynput.mouse import Controller
from pynput import mouse
from pynput import keyboard
import argparse

parser = argparse.ArgumentParser(description='set some args')
parser.add_argument('--bound', type=int, default=120)
parser.add_argument('--type', type=str, required=True)
parser.add_argument('--key', type=int, default=0)

args = parser.parse_args()

found_eyetrackers = tr.find_all_eyetrackers()
m = Controller()
length = 0
vector = (0, 0)
old = (0, 0)
new = (0, 0)

origin_pos = (0, 0)
sw = args.key

my_eyetracker = found_eyetrackers[0]
print("Address: " + my_eyetracker.address)
print("Model: " + my_eyetracker.model)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
print("Serial number: " + my_eyetracker.serial_number)


def gaze_data_callback(gaze_data):
    global gaze_pos
    global length
    global vector
    global old
    global new
    global sw

    if sw:
        gaze_left_eye = gaze_data['left_gaze_point_on_display_area']
        gaze_right_eye = gaze_data['right_gaze_point_on_display_area']

        avg_X = (gaze_left_eye[0] + gaze_right_eye[0]) / 2.0
        avg_Y = (gaze_left_eye[1] + gaze_right_eye[1]) / 2.0

        avg_X = max(min(avg_X, 1), 0)
        avg_Y = max(min(avg_Y, 1), 0)

        gaze_pos = (GetSystemMetrics(0) * avg_X, GetSystemMetrics(1) * avg_Y)
        print("gaze position: ({0})".format(gaze_pos))

        if args.type == 'lib':
            length = math.sqrt(math.pow(m.position[0] - gaze_pos[0], 2) + math.pow(m.position[1] - gaze_pos[1], 2))

        if length > args.bound:
            if args.type == 'lib':
                m.position = (gaze_pos[0], gaze_pos[1])
            elif args.type == 'con':
                m.position = (gaze_pos[0], gaze_pos[1])
                length = 0
            elif args.type == 'con-ofs':
                if old != new:
                    vector_l = math.sqrt(math.pow(vector[0], 2) + math.pow(vector[1], 2))
                    ofs_X = args.bound * vector[0] / vector_l
                    ofs_Y = args.bound * vector[1] / vector_l
                    m.position = (gaze_pos[0] - ofs_X, gaze_pos[1] + ofs_Y)
                    length = 0
                    old = new


if args.type != 'lib':
    def on_move(x, y):
        global gaze_pos
        global length
        global vector
        global old
        global new
        global sw
        if sw:
            length = math.sqrt(math.pow(m.position[0] - gaze_pos[0], 2) + math.pow(m.position[1] - gaze_pos[1], 2))
            old = new
            new = (x / 2, y / 2)
            vector = (new[0] - old[0], old[1] - new[1])

    listener = mouse.Listener(on_move=on_move)
    listener.start()


def on_press(key):
    print('alphanumeric key {0} pressed'.format(
        key))
    if key == keyboard.Key.shift:
        global origin_pos
        global sw
        if sw == 0:
            origin_pos = m.position
            sw = 1


def on_release(key):
    print('{0} released'.format(
        key))
    if key == keyboard.Key.shift:
        global origin_pos
        global sw
        m.position = origin_pos
        sw = args.key


listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

while True:
    time.sleep(0.001)
