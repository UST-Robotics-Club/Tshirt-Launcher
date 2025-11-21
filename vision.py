import math
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '4' 

import cv2
from util import *

import time
from dataclasses import dataclass

class RollingAverage:
    def __init__(self, sample_num):
        self.sample_num = sample_num
        self.current_num = 1
        self.current_index = 0
        self.samples = [0 for i in range(sample_num)]

    def put(self, x):
        self.samples[self.current_index] = x
        self.current_index += 1
        if self.current_index > self.current_num:
            self.current_num = self.current_index
        if self.current_index >= self.sample_num:
            self.current_index = 0
        return self.get()

    def clear(self):
        self.current_index = 0
        self.current_num = 1
        self.samples[0] = 0

    def get(self):
        val = 0
        for i in range(0, self.current_num):
            val += self.samples[i]
        return val / self.current_num

    def copy_from(self, other_avg):
        self.clear()
        for i in range(0, other_avg.current_num):
            self.put(other_avg.samples[i])

VERTICAL_HAND_THRESHOLD = 25 # maximum angle distance distance with which the hand and elbow are considered vertical to each other
HORIZIZONTAL_ELBOW_THRESHOLD = 20 # maximum angle distance distance with which the elbow and shoulder are considered horizontal to each other
HAND_TOUCH_THRESHOLD = 0.12 # maximum distance with which the hands are considered touching
def dummy(*args):
    pass

is_running = False
process_func = dummy

def set_running():
    global is_running
    is_running = True

def initialize():
    global is_running, process_func
    # the reason all these imports are inside here is so they can run in their own thread when vision starts up
    from mediapipe import solutions
    from mediapipe.framework.formats import landmark_pb2
    import numpy as np
    import mediapipe as mp
    def draw_landmarks_on_image(rgb_image, detection_result):
        pose_landmarks_list = detection_result.pose_landmarks
        annotated_image = np.copy(rgb_image)

        for idx in range(len(pose_landmarks_list)):
            pose_landmarks = pose_landmarks_list[idx]
            pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            pose_landmarks_proto.landmark.extend([
                landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
            ])
            style = solutions.drawing_styles.get_default_pose_landmarks_style()
            solutions.drawing_utils.draw_landmarks(
                annotated_image,
                pose_landmarks_proto,
                solutions.pose.POSE_CONNECTIONS,
                style)
        return annotated_image

    def handle_landmarks(landmarks, world_landmarks, frame):
        pass

    run = True

    BaseOptions = mp.tasks.BaseOptions
    PoseLandmarker = mp.tasks.vision.PoseLandmarker

    PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    # Create a pose landmarker instance with the video mode:
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="pose_landmarker_lite.task"),
        running_mode=VisionRunningMode.VIDEO,
        num_poses=1)
    landmarker = PoseLandmarker.create_from_options(options)
    def _process(frame, callback):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if is_running:
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            result = landmarker.detect_for_video(mp_image, timestamp_ms=int(time.time() * 1000))
            if result.pose_world_landmarks:
                landmarks = result.pose_landmarks[0]
                
                callback(landmarks, frame)
        return frame
                
    process_func = _process

class Landmark:
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32


if __name__ == "__main__":
    main()
