import numpy as np
from insightface.app import FaceAnalysis


class FaceIdentity:
    def __init__(self, similarity_threshold: float = 0.45) -> None:
        self.similarity_threshold = similarity_threshold

        self.model = FaceAnalysis(
            name="buffalo_l",
            providers=["CPUExecutionProvider"],
        )

        self.model.prepare(
            ctx_id=-1,
            det_size=(640, 640),
        )

        self.known_identities: dict[int, np.ndarray] = {}
        self.next_person_id = 1

    @staticmethod
    def _normalize(embedding: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(embedding)

        if norm == 0:
            return embedding

        return embedding / norm

    @staticmethod
    def _similarity(
        embedding_a: np.ndarray,
        embedding_b: np.ndarray,
    ) -> float:
        return float(
            np.dot(
                embedding_a,
                embedding_b,
            )
        )

    def identify(self, frame):
        faces = self.model.get(frame)

        results = []

        for face in faces:
            embedding = self._normalize(
                face.embedding
            )

            best_person_id = None
            best_similarity = -1.0

            for person_id, known_embedding in self.known_identities.items():
                similarity = self._similarity(
                    embedding,
                    known_embedding,
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_person_id = person_id

            if (
                best_person_id is not None
                and best_similarity >= self.similarity_threshold
            ):
                person_id = best_person_id

                # Slowly update stored representation.
                updated_embedding = (
                    0.90 * self.known_identities[person_id]
                    + 0.10 * embedding
                )

                self.known_identities[person_id] = self._normalize(
                    updated_embedding
                )

            else:
                person_id = self.next_person_id
                self.next_person_id += 1

                self.known_identities[person_id] = embedding

            bbox = face.bbox.astype(int)

            x1, y1, x2, y2 = bbox

            results.append(
                {
                    "person_id": person_id,
                    "bbox": (
                        int(x1),
                        int(y1),
                        int(x2 - x1),
                        int(y2 - y1),
                    ),
                    "similarity": best_similarity,
                }
            )

        return results