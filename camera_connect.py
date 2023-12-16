from picamera import PiCamera
from datetime import datetime
import time
import numpy as np
import cv2
import os
import matplotlib
import matplotlib.pyplot as plt

from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

DRIVE_SERVER_DUMP_DIR = "/Users/wanlin/Desktop/camera_images"
DRIVE_SERVER_REQUEST_EXEC = "/Users/wanlin/envs/py3/bin/python /Users/wanlin/Desktop/iot/drive_server/send_request.py"
DRIVE_SERVER_IP = "wanlin@192.168.1.27"

IMAGE_DUMP_DIR = "/home/wanlin/Desktop/camera_images"
TIMESTAMP_FORMAT = "%m_%d_%Y_%H_%M_%S_%f"

class CameraDetection:
    def __init__(
        self,
        image_dump_dir,
        img_width = 640,
        frame_rate = 4,
        detection_pixel_thresh = 1e6,
        detection_hist_thresh = 1e5,
        preview_image = False,
    ):
        self.image_dump_dir = image_dump_dir
        self.prev_hist = None
        self.background_img = None
        self.no_detection_counter = 0
        self.detection_counter = 0
        self.last_forwarding_time = datetime.now()

        self.img_width = img_width
        self.img_height = int(img_width * 0.75)
        self.frame_rate = frame_rate
        self.detection_pixel_thresh = detection_pixel_thresh
        self.detection_hist_thresh = detection_hist_thresh

        self.preview_image = preview_image

    def compute_hist(self, img):
        # compute histogram
        hist = cv2.calcHist([img], [0], None, [256], [0, 256])
        hist_flatten = hist.flatten()
        hist_x = np.array(range(256))

        hist_diff = 0
        if self.prev_hist is None:
            self.prev_hist = hist_flatten
        else:
            hist_diff = np.linalg.norm(hist_flatten - self.prev_hist)
            self.prev_hist = hist_flatten

        if self.preview_image:
            # plot histogram
            fig = matplotlib.pyplot.figure()
            ax = fig.add_subplot(111)
            ax.plot(hist_x, hist_flatten)
            fig.canvas.draw()

            image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            image_from_plot = image_from_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))

            cv2.imshow("hist", image_from_plot)
            cv2.waitKey(1)
        return hist_diff > self.detection_hist_thresh

    def substract_detection(self, img):
        # use erode to detect moving objects
        if self.background_img is None or self.no_detection_counter > 100:
            self.no_detection_counter = 0
            self.background_img = img
        diff_img = cv2.absdiff(img, self.background_img)
        thresh, binary_img = cv2.threshold(diff_img, 60, 255, cv2.THRESH_BINARY)
        erode_kernel = np.ones((3, 3), np.uint8)
        img_erode = cv2.erode(binary_img, erode_kernel)
        pixel_sum = img_erode.sum()

        if self.preview_image:
            cv2.imshow("diff_img", img_erode)
            cv2.waitKey(1)
        return pixel_sum > self.detection_pixel_thresh

    def tf_detection(self, img):
        model = "efficientdet_lite0.tflite"
        num_threads = 4
        base_options = core.BaseOptions(file_name=model, num_threads=num_threads)
        detection_options = processor.DetectionOptions(max_results=3, score_threshold=0.3)
        options = vision.ObjectDetectorOptions(base_options=base_options, detection_options=detection_options)
        detector = vision.ObjectDetector.create_from_options(options)

        input_tensor = vision.TensorImage.create_from_array(img)
        detection_result = detector.detect(input_tensor)
        return len(detection_result) > 0

    def dump_image(self, img):
        # dump image to local machine
        img_name = datetime.now().strftime(TIMESTAMP_FORMAT) + ".png"
        img_path = os.path.join(self.image_dump_dir, img_name)
        cv2.imwrite(img_path, img)
        print(f"write image to {img_path}")

    def forward_images(self):
        # forward image to drive server
        images_list = os.listdir(self.image_dump_dir)
        images_sent = 0
        for img_str in images_list:
            datetime_str = img_str.split(".")[0]
            datetime_obj = datetime.strptime(datetime_str, TIMESTAMP_FORMAT)
            if datetime_obj < self.last_forwarding_time:
                continue
            os.system(f"scp {IMAGE_DUMP_DIR}/{img_str} {DRIVE_SERVER_IP}:{DRIVE_SERVER_DUMP_DIR}")
            images_sent += 1
        print(f"**** FORWARDED {images_sent} IMAGES")

        last_forwarding_time_str = self.last_forwarding_time.strftime(TIMESTAMP_FORMAT)
        os.system(f"ssh {DRIVE_SERVER_IP} '{DRIVE_SERVER_REQUEST_EXEC} {last_forwarding_time_str}'")
        print("**** IMAGES UPLOADED TO DRIVE")
        self.last_forwarding_time = datetime.now()

    def run(self):
        with PiCamera() as camera:
            camera.resolution = (self.img_width, self.img_height)
            camera.framerate = self.frame_rate
            while True:
                time.sleep(0.2)
                image = np.empty((self.img_height * self.img_width * 3), dtype=np.uint8)
                camera.capture(image, "bgr")
                image = image.reshape((self.img_height, self.img_width, 3))
                image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                sub_det = self.substract_detection(image_gray)
                hist_det = self.compute_hist(image_gray)
                if sub_det or hist_det:
                    self.dump_image(image_gray)
                    self.detection_counter += 1
                    self.no_detection_counter = 0
                else:
                    if self.detection_counter > 0:
                        self.forward_images()
                    self.detection_counter = 0
                    self.no_detection_counter += 1
                print(f"no_detection_counter {self.no_detection_counter} detection_counter {self.detection_counter}")
                print(f"Detection {sub_det}, {hist_det}")
                if self.preview_image:
                    cv2.imshow("camera", image_gray)
                    cv2.waitKey(1)

if __name__ == "__main__":
    os.popen(f"rm {IMAGE_DUMP_DIR}/*png")
    os.popen(f"ssh {DRIVE_SERVER_IP} 'rm {DRIVE_SERVER_DUMP_DIR}/*png'")
    camera_node = CameraDetection(IMAGE_DUMP_DIR, preview_image=False)
    camera_node.run()

