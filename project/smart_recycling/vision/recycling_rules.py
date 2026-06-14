# ==================================================
# Gachon University
# Introduction to Internet of Things (13966_001)
# 2026-1 Semester Team C
#
# Recycling rules
# ==================================================
from __future__ import annotations

from dataclasses import dataclass

# recycle advice
@dataclass(frozen=True)
class RecyclingAdvice:
    category: str     
    line1: str        # label name
    line2: str        # advice
    detail: str       

RULES: dict[str, RecyclingAdvice] = {
    "battery": RecyclingAdvice(
        "battery",
        "Battery",
        "Battery Box",
        "Use a battery collection box."
    ),

    "biological": RecyclingAdvice(
        "biological",
        "Food Waste",
        "Food Bin",
        "Drain liquid and dispose as food waste."
    ),

    "cardboard": RecyclingAdvice(
        "cardboard",
        "Cardboard",
        "Paper Bin",
        "Flatten before disposal."
    ),

    "clothes": RecyclingAdvice(
        "clothes",
        "Clothes",
        "Donation Bin",
        "Donate if reusable, otherwise dispose appropriately."
    ),

    "glass": RecyclingAdvice(
        "glass",
        "Glass",
        "Glass Bin",
        "Rinse and place in the glass recycling bin."
    ),

    "metal": RecyclingAdvice(
        "metal",
        "Metal",
        "Metal Bin",
        "Rinse and place in the metal recycling bin."
    ),

    "paper": RecyclingAdvice(
        "paper",
        "Paper",
        "Paper Bin",
        "Keep dry and place in the paper recycling bin."
    ),

    "plastic": RecyclingAdvice(
        "plastic",
        "Plastic",
        "Plastic Bin",
        "Rinse and place in the plastic recycling bin."
    ),

    "trash": RecyclingAdvice(
        "trash",
        "General Waste",
        "Trash Bin",
        "Dispose as general waste."
    ),

    "vinyl": RecyclingAdvice(
        "vinyl",
        "Vinyl",
        "Vinyl Bin",
        "Clean and dry before disposal."
    ),
}

UNKNOWN_ADVICE = RecyclingAdvice(
    category="unknown",
    line1="Unknown Item",
    line2="Check label",
    detail="Could not map detection to a recycling rule. Check the item manually.",
)
NO_OBJECT_ADVICE = RecyclingAdvice(
    category="none",
    line1="No Object",
    line2="Try again",
    detail="No confident object was detected.",
)

def normalize_label(label: str) -> str:
    return label.strip().lower().replace("_", " ")

# label - advice mapping
def advice_for(label: str | None) -> RecyclingAdvice:
    if not label:
        return NO_OBJECT_ADVICE
    normalized = normalize_label(label)
    """1. search 2. replace  to _ and search 3. unknown"""
    return RULES.get(normalized, RULES.get(normalized.replace(" ", "_"), UNKNOWN_ADVICE))
