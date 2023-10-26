from fer import FER
import cv2
from statistics import mode
from collections import deque
import numpy
import sounddevice
import argparse

parser = argparse.ArgumentParser(
    description="A vtuber program with emotion recognition",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    prog="python -m is_that_you"
)
parser.add_argument("--volume-threshold", "-v", default=15, help="the amount of volume from your microphone after which the mouth will open")
parser.add_argument("--emotion-stabilization-frames-amount", "-esfa", default=10, help="the amount of recent frames that are used to calculate the most frequent emotion. This is used to prevent one-off incorrect emotion recognition. Higher numbers lead to more accurate recognition, but it will take more time for the emotion to switch")
parser.add_argument("--video-capture-device-identifier", "-vcdi", default=0, help="the identifier of the camera device that will be used for capturing emotions")
args = parser.parse_args()

detector = FER()
real_camera = cv2.VideoCapture(args.video_capture_device_identifier)
recent_emotions = deque(maxlen=args.emotion_stabilization_frames_amount)

mouth_open = False
current_emotion = "neutral"

def update_view():
    print(current_emotion, mouth_open)

def process_sound(frames: numpy.ndarray):
    global mouth_open
    volume_norm = numpy.linalg.norm(frames)
    if volume_norm > args.volume_threshold:
        if not mouth_open:
            mouth_open = True
            update_view()
    else:
        if mouth_open:
            mouth_open = False
            update_view()

microphone_input_stream = sounddevice.InputStream()
microphone_input_stream.start()

audio_frames_per_second = microphone_input_stream.samplerate

while True:
    ret, frame = real_camera.read()
    if not ret:
        break
    emotion, score = detector.top_emotion(frame)
    if emotion is not None:
        recent_emotions.append(emotion)
        probable_emotion = mode(recent_emotions)
        if current_emotion != probable_emotion:
            current_emotion = probable_emotion
            update_view()
    frames, _overflowed = microphone_input_stream.read(int(audio_frames_per_second * 0.1))
    process_sound(frames)