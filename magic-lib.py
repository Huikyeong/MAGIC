import tobii_research as tr
import time
import math
from win32api import GetSystemMetrics
from pynput.mouse import Controller
import argparse

parser = argparse.ArgumentParser(description='set threshold')
parser.add_argument('--threshold', type=int, default=120, help='an integer for printing repeatably')
parser.add_argument('--type', type=str, default='lib')

args = parser.parse_args()
# APP_TYPE = "LIB" # "cON", 


found_eyetrackers = tr.find_all_eyetrackers()
m = Controller()

my_eyetracker = found_eyetrackers[0]
print("Address: " + my_eyetracker.address)
print("Model: " + my_eyetracker.model)
print("Name (It's OK if this is empty): " + my_eyetracker.device_name)
print("Serial number: " + my_eyetracker.serial_number)


def gaze_data_callback(gaze_data):
    gaze_left_eye = gaze_data['left_gaze_point_on_display_area']
    gaze_right_eye = gaze_data['right_gaze_point_on_display_area']

    avg_X = (gaze_left_eye[0] + gaze_right_eye[0]) / 2.0
    avg_Y = (gaze_left_eye[1] + gaze_right_eye[1]) / 2.0

    avg_X = max(min(avg_X, 1), 0)
    avg_Y = max(min(avg_Y, 1), 0)

    gaze_pos = (GetSystemMetrics(0) * avg_X, GetSystemMetrics(1) * avg_Y)
    print("gaze position: ({0})".format(gaze_pos))

    length = math.sqrt(math.pow(m.position[0] - gaze_pos[0], 2) + math.pow(m.position[1] - gaze_pos[1], 2))

    if length > args.threshold:
        m.position = (gaze_pos[0], gaze_pos[1])


my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

while True:
    time.sleep(0.001)
