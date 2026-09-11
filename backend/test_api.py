import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_backend_api():
    print("Testing FastAPI Backend Endpoints...")

    # 1. Health check
    r1 = requests.get(f"{BASE_URL}/")
    print(f"Health Check: {r1.status_code} -> {r1.json()}")
    assert r1.status_code == 200

    # 2. Reagents list
    r2 = requests.get(f"{BASE_URL}/api/reagents")
    print(f"Supported Reagents: {len(r2.json()['reagents'])} reagents available")
    assert r2.status_code == 200

    # 3. Create Case Record
    case_payload = {
        "case_id": "TEST-CASE-9001",
        "officer_id": "Officer J. Doe (NCB-551)",
        "sample_id": "SAMPLE-QR-7712",
        "location": "Indira Gandhi International Airport, New Delhi",
        "reagent_used": "Marquis Reagent",
        "presumptive_category": "Opioid Class (Heroin / Morphine / Codeine)",
        "confidence_score": 98.5,
        "detected_color_description": "Deep Purple/Violet",
        "delta_e_distance": 1.2,
        "cross_reactivity_warnings": ["May cross-react with DXM."],
        "recommended_lab_confirmation": "GC-MS / HPLC for Opioid Quantitation"
    }

    r3 = requests.post(f"{BASE_URL}/api/cases/create", json=case_payload)
    print(f"Create Case API: {r3.status_code} -> Block #{r3.json()['block']['block_index']}")
    assert r3.status_code == 200

    # 4. Verify Ledger
    r4 = requests.get(f"{BASE_URL}/api/chain/verify")
    print(f"Ledger Integrity API: Valid={r4.json()['is_chain_valid']} ({r4.json()['total_records']} Blocks)")
    assert r4.json()["is_chain_valid"] is True

    print("\n[PASS] All Backend API Tests Passed!")

if __name__ == "__main__":
    test_backend_api()
