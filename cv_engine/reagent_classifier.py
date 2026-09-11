import numpy as np
from cv_engine.color_calibrator import ColorCalibrator, rgb_to_lab, ciede2000

# Standard Forensic Reagent Color Database
REAGENT_DATABASE = {
    "Marquis Reagent": [
        {
            "category": "Opioid Class (Heroin / Morphine / Codeine)",
            "expected_rgb": (80, 0, 90), # Deep Purple / Violet
            "color_name": "Deep Purple/Violet",
            "warnings": ["May cross-react with certain cough suppressants containing dextromethorphan."],
            "lab_confirm_recommended": "GC-MS / HPLC for Opioid Quantitation"
        },
        {
            "category": "Amphetamine / Methamphetamine",
            "expected_rgb": (200, 70, 0), # Orange-Red to Brown
            "color_name": "Orange-Red to Dark Brown",
            "warnings": ["Substituted phenethylamines and ephedrine may cause similar red-orange reaction."],
            "lab_confirm_recommended": "GC-MS Confirmation"
        },
        {
            "category": "MDMA / Ecstasy",
            "expected_rgb": (30, 10, 40), # Dark Violet to Black
            "color_name": "Dark Purple to Near Black",
            "warnings": ["MDA / MDEA yield identical dark purple reactions."],
            "lab_confirm_recommended": "GC-MS / FTIR Spectrometry"
        }
    ],
    "Duquenois-Levine Reagent": [
        {
            "category": "Cannabis / THC / Hashish",
            "expected_rgb": (110, 20, 130), # Violet / Purple in organic layer
            "color_name": "Violet/Purple Layer",
            "warnings": ["High chlorophyll concentrations or herbal tea extracts may interfere."],
            "lab_confirm_recommended": "HPLC / TLC Lab Analysis"
        }
    ],
    "Scott Reagent (Cobalt Thiocyanate)": [
        {
            "category": "Cocaine Hydrochloride",
            "expected_rgb": (0, 120, 200), # Turquoise / Cobalt Blue
            "color_name": "Turquoise / Cobalt Blue Flakes",
            "warnings": ["Lidocaine, procaine, and benzocaine local anesthetics can produce false positive blue precipitates."],
            "lab_confirm_recommended": "GC-MS / Raman Spectroscopy"
        }
    ],
    "Simon's Reagent": [
        {
            "category": "Secondary Amine (Methamphetamine / MDMA)",
            "expected_rgb": (0, 80, 180), # Deep Blue
            "color_name": "Deep Cobalt Blue",
            "warnings": ["Primary amines (Amphetamine) will NOT react (remain pale)."],
            "lab_confirm_recommended": "GC-MS Confirmation"
        }
    ]
}


class ReagentClassifier:
    """
    Analyzes color extracted from test spot plates and classifies presumptive drug category.
    """

    def __init__(self):
        self.calibrator = ColorCalibrator()

    def analyze_patch(self, image_patch, reagent_name="Marquis Reagent", apply_white_balance=False):
        """
        Analyzes a cropped reagent reaction image patch.
        Returns diagnostic dictionary with match result, confidence %, and warnings.
        """
        # Step 1: Apply Gray-World White Balance if whole image context provided
        if apply_white_balance:
            processed_patch = self.calibrator.apply_gray_world_white_balance(image_patch)
        else:
            processed_patch = image_patch

        # Step 2: Extract Dominant Color
        sampled_rgb = self.calibrator.extract_dominant_rgb(processed_patch)
        sampled_lab = rgb_to_lab(sampled_rgb)

        # Step 3: Match against Reagent Database
        if reagent_name not in REAGENT_DATABASE:
            return {
                "error": f"Unknown reagent: {reagent_name}",
                "supported_reagents": list(REAGENT_DATABASE.keys())
            }

        candidates = REAGENT_DATABASE[reagent_name]
        best_match = None
        min_delta_e = float('inf')

        for candidate in candidates:
            cand_lab = rgb_to_lab(candidate["expected_rgb"])
            delta_e = ciede2000(sampled_lab, cand_lab)

            if delta_e < min_delta_e:
                min_delta_e = delta_e
                best_match = candidate

        # Step 4: Calculate Confidence Score (Inverse of Delta E)
        # Delta E < 5 is visually identical, > 30 is significantly different
        max_dist = 40.0
        confidence = max(0.0, min(100.0, (1.0 - (min_delta_e / max_dist)) * 100.0))

        # Check negative/inconclusive threshold
        is_presumptive_positive = bool(confidence >= 50.0)

        if is_presumptive_positive:
            result_category = best_match["category"]
            color_desc = best_match["color_name"]
            warnings = best_match["warnings"]
            lab_confirm = best_match["lab_confirm_recommended"]
        else:
            result_category = "Negative / Inconclusive Reaction"
            color_desc = "No significant target color shift detected"
            warnings = ["Sample did not produce expected colorimetric shift for selected reagent."]
            lab_confirm = "Perform secondary reagent test or submit directly for GC-MS laboratory confirmation."

        return {
            "reagent_used": reagent_name,
            "sampled_rgb": sampled_rgb,
            "sampled_lab": [round(v, 2) for v in sampled_lab],
            "delta_e_distance": round(min_delta_e, 2),
            "confidence_score": round(confidence, 1),
            "is_presumptive_positive": is_presumptive_positive,
            "presumptive_category": result_category,
            "detected_color_description": color_desc,
            "cross_reactivity_warnings": warnings,
            "recommended_lab_confirmation": lab_confirm,
            "disclaimer": "PRESUMPTIVE RESULT ONLY — Mandatory Forensic Laboratory Confirmation Required."
        }
