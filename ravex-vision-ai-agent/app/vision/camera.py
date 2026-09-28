import time

import cv2

from app.config import settings


class Camera:
    def __init__(self) -> None:
        self.capture = None
        self.previous_time = time.perf_counter()

    def start(self) -> None:
        self.capture = cv2.VideoCapture(settings.CAMERA_INDEX)

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Unable to open camera index {settings.CAMERA_INDEX}"
            )

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            settings.CAMERA_WIDTH,
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            settings.CAMERA_HEIGHT,
        )

        self.capture.set(
            cv2.CAP_PROP_FPS,
            settings.CAMERA_FPS,
        )

    def read(self):
        if self.capture is None:
            raise RuntimeError("Camera has not been started.")

        success, frame = self.capture.read()

        if not success:
            raise RuntimeError("Unable to read frame from camera.")

        return frame

    def calculate_fps(self) -> float:
        current_time = time.perf_counter()
        elapsed = current_time - self.previous_time
        self.previous_time = current_time

        if elapsed <= 0:
            return 0.0

        return 1.0 / elapsed

    def stop(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None