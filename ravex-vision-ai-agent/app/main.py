import cv2

from app.config import settings
from app.vision.camera import Camera


def run() -> None:
    camera = Camera()

    try:
        camera.start()

        print(f"{settings.APP_NAME} started.")
        print("Press 'q' to quit.")

        while True:
            frame = camera.read()

            fps = camera.calculate_fps()

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(settings.APP_NAME, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nApplication stopped by user.")

    finally:
        camera.stop()
        cv2.destroyAllWindows()
        print("Camera released successfully.")


if __name__ == "__main__":
    run()