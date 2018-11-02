from argparse import ArgumentParser
from collections import Counter
from time import sleep
from sys import stderr

import cv2
import numpy as np
from pyzbar import pyzbar

from virtualkeyboard import VirtualKeyboard
from systemmetrics import SystemMetrics

parser = ArgumentParser(description="Get barcode from video feed")
parser.add_argument("-c", "--camera_id", dest="camera_id", default=0, type=int, help="ID for the video feed (default: use standart camera)")
parser.add_argument("-da", "--disable_abort", dest="disable_abort", action="store_true", help="Disable closing the videofeed with esc or lmb (WARNING: Has to be killed if no code is found) (default: don't abort it)")
parser.add_argument("-m", "--mirror", dest="mirror", action="store_true", help="Invert video feed, along y-axis")
parser.add_argument("-f", "--fullscreen", dest="fullscreen", action="store_true", help="Display fullscreen if true else display window")
args = parser.parse_args()
camera_id = args.camera_id
disable_abort = args.disable_abort
mirror = args.mirror
fullscreen = args.fullscreen


def rect_transformation(x, y, width, height):
    """Transform rectangle of type "origin + size" to "two-point"
    Args:
        x (int): x coordinate of origin
        y (int): y coordinate of origin
        width (int): width of rectangle
        height (int): height of rectangle
    Returns:
        Tuple of tuple of int with x-y-coordinate pairs for both points
    """
    return ((x, y), (x + width, y + height))

class CantOpenCameraException(Exception):
    def __init__(self, camera_id):
        super().__init__(self)
        self.args[0] = f"Unable to open Camera {camera_id}"

class Camera():
    """Context Manager for video streams
    """
    def __init__(self, camera_id=0):
        self.camera_id = camera_id

    def __enter__(self):
        self.camera = cv2.VideoCapture(self.camera_id)
        if not self.camera.isOpened():
            raise CantOpenCameraException(self.camera_id)
        return self.camera

    def __exit__(self, exc_type, exc_value, traceback):
        self.camera.release()

def abort(event=cv2.EVENT_LBUTTONDOWN, x=None, y=None, flags=None, param=None):
    if event == cv2.EVENT_LBUTTONDOWN:
        stderr.write("Aborted")
        cv2.destroyAllWindows()

def cv2_setup(window):
    global disable_abort
    if fullscreen:
        cv2.namedWindow(window, cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty(window,cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    else:
        cv2.namedWindow(window)
        width, height = cv2.getWindowImageRect(window)[2:]
        cv2.moveWindow(window, (SystemMetrics.screen_width - width) // 2, (SystemMetrics.screen_height - height) // 2)
    if not disable_abort:
        cv2.setMouseCallback(window, abort)
    return window

def find_and_mark_barcodes(frame, counter):
    barcodes = pyzbar.decode(frame)
    found_codes = []
    for barcode in barcodes:
        barcode_information = (barcode.type, barcode.data.decode("utf-8"))
        counter.append(barcode_information[1])
        if barcode_information not in found_codes:
            found_codes.append(barcode_information)
            # print("Found {} barcode: {}".format(*found_codes[-1]))
        poly = barcode.polygon
        poly = np.asarray([(point.x, point.y) for point in poly])
        poly = poly.reshape((-1,1,2))
        cv2.polylines(frame, [poly] ,True, (0,255,0), 2)
        cv2.rectangle(frame, *rect_transformation(*barcode.rect), (255, 0, 0), 2)
        x, y = barcode.rect[:2]
        cv2.putText(frame, "{}({})".format(*barcode_information), (x, y-10), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 1)
    return frame, counter

def main(window, camera):
    counter = []
    while True:
        frame = camera.read()[1]
        marked_frame, counter = find_and_mark_barcodes(frame, counter)
        # marked_frame = cv2.resize(frame, (SystemMetrics.screen_width, SystemMetrics.screen_height))
        if mirror:
            marked_frame = cv2.flip(marked_frame, 1)
        cv2.imshow(window, marked_frame)
        key = cv2.waitKey(1)

        if cv2.getWindowProperty(window, 0) < 0: # prevent window reopening after closing via [x]
            return
        if not disable_abort:
            if key == 27: # key 27 = esc
                abort()
                return
        
        if counter:
            code = Counter(counter).most_common(1)[0]
            if code[1] > 20:
                print(code[0])
                cv2.destroyWindow(window)
                sleep(5)
                VirtualKeyboard.print(str(code[0]))
                return

try:
    mirror = True
    fullscreen = True
    with Camera(camera_id) as camera:
        window = cv2_setup("SV Barcode Reader")
        main(window, camera)
except IOError as err:
    stderr.write(err.args[0])
cv2.destroyWindow(window)