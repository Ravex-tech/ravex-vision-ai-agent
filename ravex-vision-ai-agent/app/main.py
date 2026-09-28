import cv2
import time

from app.vision.camera import Camera
from app.vision.face_identity import FaceIdentity


WINDOW_NAME = "RAVEX VISION AI"


def main():
    camera = Camera()
    camera.start()
    face_identity = FaceIdentity(
        similarity_threshold=0.45
    )

    previous_time = time.time()

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Unable to read camera frame.")
                break

            identities = face_identity.identify(frame)

            current_time = time.time()

            elapsed = current_time - previous_time

            fps = (
                1 / elapsed
                if elapsed > 0
                else 0
            )

            previous_time = current_time

            for identity in identities:
                x, y, width, height = identity["bbox"]

                person_id = identity["person_id"]

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + width, y + height),
                    (255, 255, 255),
                    2,
                )

                cv2.putText(
                    frame,
                    f"Person {person_id:02d}",
                    (x, max(y - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2,
                )

            cv2.putText(
                frame,
                "RAVEX VISION AI",
                (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.putText(
                frame,
                f"Persons: {len(identities)}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

            cv2.imshow(
                WINDOW_NAME,
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

            if (
                cv2.getWindowProperty(
                    WINDOW_NAME,
                    cv2.WND_PROP_VISIBLE,
                )
                < 1
            ):
                break

    except KeyboardInterrupt:
        print("Application interrupted by user.")

    finally:
      try:
          camera.release()
      except Exception:
          pass

      cv2.destroyAllWindows()
      print("Camera released successfully.")


if __name__ == "__main__":
    main()