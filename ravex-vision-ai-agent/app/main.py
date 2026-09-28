import cv2
import time

from app.vision.camera import Camera
from app.vision.face_identity import FaceIdentity


WINDOW_NAME = "RAVEX VISION AI"

# Run expensive InsightFace inference only once every N frames.
RECOGNITION_INTERVAL = 10


def main():
    camera = Camera()
    camera.start()

    face_identity = FaceIdentity(
        similarity_threshold=0.45
    )

    frame_count = 0
    identities = []

    previous_time = time.perf_counter()

    # Smoothed FPS instead of unstable single-frame FPS.
    smoothed_fps = 0.0

    try:
        while True:
            frame = camera.read()

            if frame is None:
                print("Unable to read camera frame.")
                break

            frame_count += 1

            # -------------------------------------------------
            # EXPENSIVE AI INFERENCE
            # Only run InsightFace periodically.
            # -------------------------------------------------
            if (
                frame_count == 1
                or frame_count % RECOGNITION_INTERVAL == 0
            ):
                identities = face_identity.identify(frame)

            # -------------------------------------------------
            # FPS calculation
            # -------------------------------------------------
            current_time = time.perf_counter()
            elapsed = current_time - previous_time
            previous_time = current_time

            if elapsed > 0:
                current_fps = 1.0 / elapsed

                if smoothed_fps == 0:
                    smoothed_fps = current_fps
                else:
                    smoothed_fps = (
                        0.90 * smoothed_fps
                        + 0.10 * current_fps
                    )

            # -------------------------------------------------
            # Draw identities from latest recognition result.
            # -------------------------------------------------
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

            # -------------------------------------------------
            # UI
            # -------------------------------------------------
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
                f"FPS: {smoothed_fps:.1f}",
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

            cv2.putText(
                frame,
                f"Recognition: 1/{RECOGNITION_INTERVAL} frames",
                (20, 130),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.55,
                (255, 255, 255),
                1,
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