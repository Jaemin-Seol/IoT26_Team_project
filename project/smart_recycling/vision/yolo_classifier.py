from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import cv2
import time

from smart_recycling.vision.recycling_rules import RecyclingAdvice, advice_for

@dataclass(frozen=True)
class ClassificationResult:
    matched_label: str | None
    confidence: float | None
    class_id: int | None
    advice: RecyclingAdvice
    annotated_path: Path


class YoloClassifier:
    def __init__(self, model_path: str, confidence: float = 0.35, imgsz: int = 640, top_k: int = 5) -> None:
        self.model_path = model_path
        self.confidence = confidence
        self.imgsz = imgsz
        self._model = None

    # load the YOLO model on first use
    @property
    def model(self):
        if self._model is None:
            from ultralytics import YOLO

            from pathlib import Path
            print("cwd =", Path.cwd())
            print("model =", self.model_path)
            print("exists =", Path(self.model_path).exists())
            print("absolute =", Path(self.model_path).resolve())
            self._model = YOLO(self.model_path)
        return self._model

    # Run inference and generate an annotated result image
    def classify(self, image: Any, output_dir: Path) -> ClassificationResult:
        #LABEL alias to correct typo
        LABEL_ALIASES = {
            "vynil": "vinyl",
        }
        # Prepare output directory for result image.
        output_dir.mkdir(parents=True, exist_ok=True)

        # Run YOLO classification inference.
        results = self.model.predict(
            source=image,
            imgsz=self.imgsz,
            verbose=False,
        )
        result = results[0]

        # Classification models return probabilities in result.probs.
        probs = result.probs
        if probs is None:
            raise RuntimeError(
                "Model did not return classification probabilities. "
                "Please check that the loaded model is a YOLO classification model."
            )

        # Get the most probable class.
        top1_id = int(probs.top1)
        label = str(self.model.names[top1_id])
        confidence = float(probs.data[top1_id])

        # Fix known label typos from the trained model.
        label = LABEL_ALIASES.get(label, label)

        # Apply confidence threshold.
        if confidence >= self.confidence:
            matched_label = label
            matched_confidence = confidence
            matched_class_id = top1_id
        else:
            matched_label = None
            matched_confidence = None
            matched_class_id = None

        # Convert label into recycling advice.
        advice = advice_for(matched_label)

        # Save visualized classification result.
        annotated_path = output_dir / f"annotated_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
        cv2.imwrite(str(annotated_path), result.plot())

        return ClassificationResult(
            matched_label=matched_label,
            confidence=matched_confidence,
            class_id=matched_class_id,
            advice=advice,
            annotated_path=annotated_path,
        )
