from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from smart_recycling.vision.recycling_rules import RecyclingAdvice, advice_for


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    class_id: int


@dataclass(frozen=True)
class ClassificationResult:
    matched_label: str | None
    advice: RecyclingAdvice
    detections: list[Detection]
    annotated_path: Path


class YoloClassifier:
    def __init__(self, model_path: str, confidence: float = 0.35, imgsz: int = 640, top_k: int = 5) -> None:
        self.model_path = model_path
        self.confidence = confidence
        self.imgsz = imgsz
        self.top_k = top_k
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from ultralytics import YOLO

            self._model = YOLO(self.model_path)
        return self._model

    def classify(self, image: Any, output_dir: Path) -> ClassificationResult:
        import cv2
        import time

        output_dir.mkdir(parents=True, exist_ok=True)
        results = self.model.predict(source=image, imgsz=self.imgsz, conf=self.confidence, verbose=False)
        result = results[0]

        detections: list[Detection] = []
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = str(self.model.names[class_id])
            confidence = float(box.conf[0])
            detections.append(Detection(label=label, confidence=confidence, class_id=class_id))
        detections.sort(key=lambda item: item.confidence, reverse=True)
        detections = detections[: self.top_k]

        matched_label = self._choose_label(detections)
        advice = advice_for(matched_label)

        annotated_path = output_dir / f"annotated_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(str(annotated_path), result.plot())
        return ClassificationResult(
            matched_label=matched_label,
            advice=advice,
            detections=detections,
            annotated_path=annotated_path,
        )

    @staticmethod
    def _choose_label(detections: list[Detection]) -> str | None:
        if not detections:
            return None
        for detection in detections:
            advice = advice_for(detection.label)
            if advice.category != "unknown":
                return detection.label
        return detections[0].label
