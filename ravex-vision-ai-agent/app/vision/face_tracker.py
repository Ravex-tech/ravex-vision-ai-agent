from dataclasses import dataclass
from math import hypot


@dataclass
class Track:
    track_id: int
    bbox: tuple[int, int, int, int]
    center: tuple[int, int]
    missed_frames: int = 0
    hits: int = 1


class FaceTracker:
    def __init__(
        self,
        max_distance: float = 220.0,
        max_missed_frames: int = 45,
        min_iou: float = 0.05,
    ) -> None:
        self.next_id = 1
        self.tracks: dict[int, Track] = {}

        self.max_distance = max_distance
        self.max_missed_frames = max_missed_frames
        self.min_iou = min_iou

    @staticmethod
    def _center(bbox):
        x, y, w, h = bbox
        return x + w // 2, y + h // 2

    @staticmethod
    def _iou(box_a, box_b) -> float:
        ax, ay, aw, ah = box_a
        bx, by, bw, bh = box_b

        x1 = max(ax, bx)
        y1 = max(ay, by)
        x2 = min(ax + aw, bx + bw)
        y2 = min(ay + ah, by + bh)

        intersection_width = max(0, x2 - x1)
        intersection_height = max(0, y2 - y1)

        intersection = intersection_width * intersection_height

        if intersection == 0:
            return 0.0

        area_a = aw * ah
        area_b = bw * bh

        union = area_a + area_b - intersection

        if union <= 0:
            return 0.0

        return intersection / union

    def _match_score(self, track: Track, detection) -> float | None:
        detection_bbox = detection["bbox"]
        detection_center = detection["center"]

        distance = hypot(
            track.center[0] - detection_center[0],
            track.center[1] - detection_center[1],
        )

        iou = self._iou(
            track.bbox,
            detection_bbox,
        )

        # Reject detections that are too far from the previous position.
        if distance > self.max_distance and iou < self.min_iou:
            return None

        # Lower score = better match.
        distance_score = distance / self.max_distance
        iou_score = 1.0 - iou

        return (0.55 * distance_score) + (0.45 * iou_score)

    def update(self, faces):
        detections = []

        for face in faces:
            bbox = tuple(int(value) for value in face)

            detections.append(
                {
                    "bbox": bbox,
                    "center": self._center(bbox),
                }
            )

        candidates = []

        for track_id, track in self.tracks.items():
            for detection_index, detection in enumerate(detections):

                score = self._match_score(
                    track,
                    detection,
                )

                if score is not None:
                    candidates.append(
                        (
                            score,
                            track_id,
                            detection_index,
                        )
                    )

        candidates.sort(key=lambda item: item[0])

        matched_tracks = set()
        matched_detections = set()

        for _, track_id, detection_index in candidates:

            if track_id in matched_tracks:
                continue

            if detection_index in matched_detections:
                continue

            track = self.tracks[track_id]
            detection = detections[detection_index]

            track.bbox = detection["bbox"]
            track.center = detection["center"]
            track.missed_frames = 0
            track.hits += 1

            matched_tracks.add(track_id)
            matched_detections.add(detection_index)

        # Increment missed count for tracks not seen in this frame.
        for track_id, track in self.tracks.items():
            if track_id not in matched_tracks:
                track.missed_frames += 1

        # Remove tracks only after a meaningful absence.
        expired_tracks = [
            track_id
            for track_id, track in self.tracks.items()
            if track.missed_frames > self.max_missed_frames
        ]

        for track_id in expired_tracks:
            del self.tracks[track_id]

        # New ID only for genuinely unmatched detections.
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

        # Only return faces visible in the current frame.
        return sorted(
            (
                track
                for track in self.tracks.values()
                if track.missed_frames == 0
            ),
            key=lambda track: track.track_id,
        )