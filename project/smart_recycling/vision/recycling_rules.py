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
    # Waste-specific labels for a future custom model.
    # plastic
    "plastic": RecyclingAdvice("plastic", "Plastic", "Rinse first", "Rinse and put into plastic bin."),
    "plastic_bottle": RecyclingAdvice("plastic", "PET Bottle", "Cap off", "Remove cap/label, rinse, and put into PET bin."),
    "pet": RecyclingAdvice("plastic", "PET Bottle", "Cap off", "Remove cap/label, rinse, and put into PET bin."),
    # Can
    "can": RecyclingAdvice("metal", "Can", "Metal bin", "Empty, rinse, and put into metal can bin."),
    "aluminum_can": RecyclingAdvice("metal", "Can", "Metal bin", "Empty, rinse, and put into metal can bin."),
    "steel_can": RecyclingAdvice("metal", "Can", "Metal bin", "Empty, rinse, and put into metal can bin."),
    # paper
    "paper": RecyclingAdvice("paper", "Paper", "Keep dry", "Keep dry and put into paper bin."),
    "cardboard": RecyclingAdvice("paper", "Cardboard", "Flatten", "Flatten and put into paper/cardboard bin."),
    # glass
    "glass": RecyclingAdvice("glass", "Glass", "Glass bin", "Rinse and put into glass bin."),
    "glass_bottle": RecyclingAdvice("glass", "Glass Bottle", "Glass bin", "Rinse and put into glass bin."),
    # food waste
    "food_waste": RecyclingAdvice("food", "Food Waste", "Drain liquid", "Drain liquid and put into food-waste bin."),
    # battery or electornics
    "battery": RecyclingAdvice("battery", "Battery", "Recycle box", "Use a battery collection box."),
    "electronics": RecyclingAdvice("e_waste", "E-Waste", "Collect box", "Use an e-waste collection box."),
    # COCO labels from yolov8n.pt. These are demo mappings, not material proof.
    # demo
    "bottle": RecyclingAdvice("plastic", "Bottle", "Check PET", "If it is PET, remove cap/label and rinse."),
    "cup": RecyclingAdvice("unknown", "Cup", "Check material", "Check if paper, plastic, or general waste."),
    "wine glass": RecyclingAdvice("glass", "Glassware", "Usually trash", "Broken glassware is usually non-recyclable."),
    "book": RecyclingAdvice("paper", "Book/Paper", "Paper bin", "Remove coated covers if needed."),
    "cell phone": RecyclingAdvice("e_waste", "E-Waste", "Collect box", "Use an e-waste collection box."),
    "laptop": RecyclingAdvice("e_waste", "E-Waste", "Collect box", "Use an e-waste collection box."),
    "keyboard": RecyclingAdvice("e_waste", "E-Waste", "Collect box", "Use an e-waste collection box."),
    "mouse": RecyclingAdvice("e_waste", "E-Waste", "Collect box", "Use an e-waste collection box."),
    "remote": RecyclingAdvice("e_waste", "E-Waste", "Collect box", "Use an e-waste collection box."),
    "banana": RecyclingAdvice("food", "Food Waste", "Drain liquid", "Drain liquid and put into food-waste bin."),
    "apple": RecyclingAdvice("food", "Food Waste", "Drain liquid", "Drain liquid and put into food-waste bin."),
    "orange": RecyclingAdvice("food", "Food Waste", "Drain liquid", "Drain liquid and put into food-waste bin."),
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
