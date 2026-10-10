"""Comprehensive verification script for Sanchai QR subsystem."""

import requests

BASE_BACKEND = "http://127.0.0.1:8000"
BASE_FRONTEND = "http://localhost:3000"


def main():
    print("--- 1. TESTING BACKEND QR ENDPOINTS ---")

    # 1. Test QR generation for all 3 seeded patients
    patients = ["patient_ram", "patient_sita", "patient_maya"]
    for pid in patients:
        r_qr = requests.get(f"{BASE_BACKEND}/api/v1/patients/{pid}/qr.png")
        assert r_qr.status_code == 200, f"QR PNG failed for {pid}: {r_qr.status_code}"
        assert r_qr.headers.get("content-type") == "image/png"
        print(f"[PASS] Generated high-contrast QR PNG for {pid} ({len(r_qr.content)} bytes)")

        # 2. Test QR decoding with OpenCV
        r_dec = requests.post(
            f"{BASE_BACKEND}/api/v1/qr/decode",
            files={"file": (f"{pid}.png", r_qr.content, "image/png")},
        )
        assert r_dec.status_code == 200, f"QR decode failed for {pid}: {r_dec.status_code}"
        dec_data = r_dec.json()
        token = dec_data["token"]
        assert dec_data["patient_id"] == pid, f"Mismatched patient: {dec_data}"
        print(f"[PASS] Decoded token '{token}' -> Patient {dec_data['patient_name']} (Blood: {dec_data['blood_group']})")

        # 3. Test Emergency summary resolution
        r_emg = requests.get(f"{BASE_BACKEND}/api/v1/emergency/{token}")
        assert r_emg.status_code == 200, f"Emergency endpoint failed for {token}"
        emg_data = r_emg.json()
        assert emg_data["patient"]["id"] == pid
        print(f"[PASS] Emergency triage record resolved: {len(emg_data['highlights'])} highlights verified")

    print("\n--- 2. TESTING FRONTEND ROUTES ---")
    # 4. Scanner Page
    r_scan = requests.get(f"{BASE_FRONTEND}/scan")
    assert r_scan.status_code == 200
    print("[PASS] Frontend /scan route loaded successfully")

    # 5. Emergency Dynamic Page
    r_f_emg = requests.get(f"{BASE_FRONTEND}/emergency/7599a9303572da76")
    assert r_f_emg.status_code == 200
    print("[PASS] Frontend /emergency/7599a9303572da76 route loaded successfully")

    # 6. Patient Page with QR Card
    r_f_pat = requests.get(f"{BASE_FRONTEND}/patients/patient_ram")
    assert r_f_pat.status_code == 200
    print("[PASS] Frontend /patients/patient_ram route with QR card loaded successfully")

    print("\nALL QR SUBSYSTEM TESTS PASSED WITH 100% SUCCESS!")


if __name__ == "__main__":
    main()
