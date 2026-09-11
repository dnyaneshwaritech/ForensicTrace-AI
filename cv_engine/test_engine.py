import numpy as np
import cv2
from cv_engine.reagent_classifier import ReagentClassifier

def test_reagent_classification():
    classifier = ReagentClassifier()

    # Create a synthetic image patch representing a Marquis Reagent test reacting to Opioids (Deep Purple RGB ~ 80, 0, 90)
    # Note OpenCV uses BGR format
    purple_bgr_patch = np.zeros((100, 100, 3), dtype=np.uint8)
    purple_bgr_patch[:, :] = [90, 0, 80] # B=90, G=0, R=80 -> Purple

    result = classifier.analyze_patch(purple_bgr_patch, reagent_name="Marquis Reagent")
    print("--- Test 1: Opioid Marquis Test ---")
    print(f"Presumptive Result: {result['presumptive_category']}")
    print(f"Confidence Score: {result['confidence_score']}%")
    print(f"Delta E Distance: {result['delta_e_distance']}")
    assert result["is_presumptive_positive"] is True
    assert "Opioid" in result["presumptive_category"]

    # Test 2: Cocaine Scott Reagent test (Turquoise/Cobalt Blue BGR ~ 200, 120, 0)
    blue_bgr_patch = np.zeros((100, 100, 3), dtype=np.uint8)
    blue_bgr_patch[:, :] = [200, 120, 0] # B=200, G=120, R=0 -> Cobalt Blue

    result_scott = classifier.analyze_patch(blue_bgr_patch, reagent_name="Scott Reagent (Cobalt Thiocyanate)")
    print("\n--- Test 2: Cocaine Scott Test ---")
    print(f"Presumptive Result: {result_scott['presumptive_category']}")
    print(f"Confidence Score: {result_scott['confidence_score']}%")
    assert result_scott["is_presumptive_positive"] is True
    assert "Cocaine" in result_scott["presumptive_category"]

    print("\n[PASS] All CV Engine Tests Passed Successfully!")

if __name__ == "__main__":
    test_reagent_classification()
