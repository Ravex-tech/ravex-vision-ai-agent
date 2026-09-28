import cv2

from app.config import settings
from app.vision.camera import Camera
from app.vision.face_detector import FaceDetector
from app.vision.face_tracker import FaceTracker


WINDOW_NAME = "Ravex Vision AI Agent"


def run() -> None:
    camera = Camera()
    face_detector = FaceDetector()
    face_tracker = FaceTracker()

    try:
        camera.start()

        cv2.namedWindow(
            WINDOW_NAME,
            cv2.WINDOW_NORMAL,
        )

        print(f"{settings.APP_NAME} started.")
        print("Press 'q' in the video window to quit.")

        while True:
            frame = camera.read()

            faces = face_detector.detect(frame)

            tracks = face_tracker.update(faces)

            for track in tracks:
                x, y, width, height = track.bbox

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Person {track.track_id:02d}",
                    (x, max(y - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            # Calculate FPS
            fps = camera.calculate_fps()

            # Display application name
            cv2.putText(
                frame,
                "RAVEX VISION AI",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
            )

            # Display FPS
            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            # Display number of detected faces
            cv2.putText(
                frame,
                f"Persons: {len(tracks)}",
                (20, 115),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            # Exit using Q
            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            # Exit when user closes the window using X
            try:
                window_visible = cv2.getWindowProperty(
                    WINDOW_NAME,
                    cv2.WND_PROP_VISIBLE,
                )

                if window_visible < 1:
                    break

            except cv2.error:
                break

    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")

    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("Camera released successfully.")


if __name__ == "__main__":
    run()