from dataclasses import dataclass
from math import hypot


@dataclass
class Track:
    track_id: int
    bbox: tuple[int, int, int, int]
    center: tuple[int, int]
    missed_frames: int = 0


class FaceTracker:
    def __init__(
        self,
        max_distance: int = 150,
        max_missed_frames: int = 20,
    ) -> None:
        self.next_id = 1
        self.tracks: dict[int, Track] = {}

        self.max_distance = max_distance
        self.max_missed_frames = max_missed_frames

    @staticmethod
    def _get_center(bbox):
        x, y, width, height = bbox

        center_x = x + width // 2
        center_y = y + height // 2

        return center_x, center_y

    def update(self, faces):
        detections = []

        for face in faces:
            bbox = tuple(int(value) for value in face)
            center = self._get_center(bbox)

            detections.append(
                {
                    "bbox": bbox,
                    "center": center,
                }
            )

        matched_tracks = set()
        matched_detections = set()

        candidates = []

        for track_id, track in self.tracks.items():
            for detection_index, detection in enumerate(detections):

                distance = hypot(
                    track.center[0] - detection["center"][0],
                    track.center[1] - detection["center"][1],
                )

                if distance <= self.max_distance:
                    candidates.append(
                        (
                            distance,
                            track_id,
                            detection_index,
                        )
                    )

        # Closest valid matches get priority.
        candidates.sort(key=lambda item: item[0])

        for _, track_id, detection_index in candidates:

            if track_id in matched_tracks:
                continue

            if detection_index in matched_detections:
                continue

            detection = detections[detection_index]
            track = self.tracks[track_id]

            track.bbox = detection["bbox"]
            track.center = detection["center"]
            track.missed_frames = 0

            matched_tracks.add(track_id)
            matched_detections.add(detection_index)

        # Create a new persistent ID for unmatched faces.
        for detection_index, detection in enumerate(detections):

            if detection_index in matched_detections:
                continue

            track_id = self.next_id
            self.next_id += 1

            self.tracks[track_id] = Track(
                track_id=track_id,
                bbox=detection["bbox"],
                center=detection["center"],
            )

            matched_tracks.add(track_id)

        # Keep tracks temporarily when detection is lost.
        tracks_to_remove = []

        for track_id, track in self.tracks.items():

            if track_id not in matched_tracks:
                track.missed_frames += 1

            if track.missed_frames > self.max_missed_frames:
                tracks_to_remove.append(track_id)

        for track_id in tracks_to_remove:
            del self.tracks[track_id]

        # Return only people detected in the current frame.
        visible_tracks = [
            track
            for track in self.tracks.values()
            if track.missed_frames == 0
        ]

        return visible_tracks