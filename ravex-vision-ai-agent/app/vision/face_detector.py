import cv2


class FaceDetector:
    def __init__(self) -> None:
        cascade_path = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            raise RuntimeError(
                "Unable to load OpenCV face detection model."
            )

    def detect(self, frame):
        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        faces = self.face_cascade.detectMultiScale(
            gray_frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )

        return faces

    @staticmethod
    def draw(frame, faces) -> None:
        for index, (x, y, width, height) in enumerate(
            faces,
            start=1,
        ):
            cv2.rectangle(
                frame,
                (x, y),
                (x + width, y + height),
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Face {index}",
                (x, max(y - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )