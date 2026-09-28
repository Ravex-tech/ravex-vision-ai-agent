import cv2

from app.config import settings
from app.vision.camera import Camera
from app.vision.face_detector import FaceDetector


WINDOW_NAME = "Ravex Vision AI Agent"


def run() -> None:
    camera = Camera()
    face_detector = FaceDetector()

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

            # Detect faces
            faces = face_detector.detect(frame)

            # Draw face bounding boxes
            face_detector.draw(frame, faces)

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
                f"Faces: {len(faces)}",
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