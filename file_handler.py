import os
from datetime import datetime

DATA_DIR          = "data"
PATIENTS_FILE     = os.path.join(DATA_DIR, "patients.txt")
APPOINTMENTS_FILE = os.path.join(DATA_DIR, "appointments.txt")
BILLS_FILE        = os.path.join(DATA_DIR, "bills.txt")


def _ensure_data_dir() -> None:
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)


def save_patient(patient) -> str:
    _ensure_data_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # patient.to_record() already ends with "\n"
    with open(PATIENTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}|{patient.to_record()}")
    return PATIENTS_FILE


def load_patients() -> list[dict]:
    if not os.path.isfile(PATIENTS_FILE):
        return []

    records = []
    with open(PATIENTS_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            parts = raw.strip().split("|")
            if len(parts) < 13:
                continue
            records.append({
                "saved_at":      parts[0],
                "patient_id":    parts[1],
                "name":          parts[2],
                "age":           parts[3],
                "gender":        parts[4],
                "phone":         parts[5],
                "temperature":   parts[6],
                "pain_level":    parts[7],
                "heart_rate":    parts[8],
                "weight":        parts[9],
                "height":        parts[10],
                "urgency_score": parts[11],
                "urgency_label": parts[12],
            })
    return records


def save_appointment(doctor_name: str, appointment) -> str:
    _ensure_data_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    urgent    = "URGENT" if appointment.is_urgent else "NORMAL"
    line = (
        f"{timestamp}|{appointment.appointment_id}|{doctor_name}|"
        f"{appointment.patient_name}|{appointment.date}|{appointment.time}|"
        f"{appointment.reason}|{urgent}\n"
    )
    with open(APPOINTMENTS_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    return APPOINTMENTS_FILE


def load_appointments() -> list[dict]:
    if not os.path.isfile(APPOINTMENTS_FILE):
        return []

    records = []
    with open(APPOINTMENTS_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            parts = raw.strip().split("|")
            if len(parts) < 8:
                continue
            records.append({
                "saved_at":       parts[0],
                "appointment_id": parts[1],
                "doctor":         parts[2],
                "patient":        parts[3],
                "date":           parts[4],
                "time":           parts[5],
                "reason":         parts[6],
                "urgency":        parts[7],
            })
    return records


def save_bill(billing) -> str:
    _ensure_data_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # bmi / bmi_category only exist on HealthMetrics, not on plain Billing
    bmi_value = getattr(billing, "bmi", "")
    bmi_cat   = getattr(billing, "bmi_category", "")
    if bmi_value != "":
        bmi_value = f"{bmi_value:.1f}"

    line = (
        f"{timestamp}|{billing.consultation.patient_name}|"
        f"{billing.consultation.doctor_name}|"
        f"{billing.consultation.consult_type}|"
        f"{billing.consultation.fee:.2f}|"
        f"{billing.medicine.total_after_discount:.2f}|"
        f"{billing.subtotal:.2f}|"
        f"{'YES' if billing.has_insurance else 'NO'}|"
        f"{billing.insurance_discount:.2f}|"
        f"{billing.tax_amount:.2f}|"
        f"{billing.total:.2f}|"
        f"{bmi_value}|{bmi_cat}\n"
    )
    with open(BILLS_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    return BILLS_FILE


def load_bills() -> list[dict]:
    if not os.path.isfile(BILLS_FILE):
        return []

    records = []
    with open(BILLS_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            parts = raw.strip().split("|")
            if len(parts) < 11:
                continue
            records.append({
                "saved_at":       parts[0],
                "patient":        parts[1],
                "doctor":         parts[2],
                "consult_type":   parts[3],
                "consult_fee":    parts[4],
                "medicine_total": parts[5],
                "subtotal":       parts[6],
                "has_insurance":  parts[7],
                "insurance_off":  parts[8],
                "tax":            parts[9],
                "total":          parts[10],
                "bmi":            parts[11] if len(parts) > 11 else "",
                "bmi_category":   parts[12] if len(parts) > 12 else "",
            })
    return records


def print_saved_patients() -> None:
    rows = load_patients()
    if not rows:
        print("\n  (No patients have been saved yet.)\n")
        return
    print(f"\n  Saved patients : {len(rows)}")
    print("  " + "-" * 78)
    print(f"  {'ID':<10} {'Name':<22} {'Age':>3}  {'Urgency':<12} {'Saved at':<19}")
    print("  " + "-" * 78)
    for r in rows:
        print(f"  {r['patient_id']:<10} {r['name'][:22]:<22} {r['age']:>3}  "
              f"{r['urgency_label'].strip():<12} {r['saved_at']:<19}")
    print("  " + "-" * 78)


def print_saved_appointments() -> None:
    rows = load_appointments()
    if not rows:
        print("\n  (No appointments have been saved yet.)\n")
        return
    print(f"\n  Saved appointments : {len(rows)}")
    print("  " + "-" * 78)
    print(f"  {'ID':<8} {'Patient':<18} {'Doctor':<18} {'Date':<11} {'Time':<6} {'Urgency':<7}")
    print("  " + "-" * 78)
    for r in rows:
        print(f"  {r['appointment_id']:<8} {r['patient'][:18]:<18} "
              f"{r['doctor'][:18]:<18} {r['date']:<11} {r['time']:<6} {r['urgency']:<7}")
    print("  " + "-" * 78)


def print_saved_bills() -> None:
    rows = load_bills()
    if not rows:
        print("\n  (No bills have been saved yet.)\n")
        return
    print(f"\n  Saved bills : {len(rows)}")
    print("  " + "-" * 78)
    print(f"  {'Patient':<22} {'Doctor':<18} {'Subtotal':>12} {'Total':>12} {'Ins':<4}")
    print("  " + "-" * 78)
    for r in rows:
        print(f"  {r['patient'][:22]:<22} {r['doctor'][:18]:<18} "
              f"{float(r['subtotal']):>12,.0f} {float(r['total']):>12,.0f} {r['has_insurance']:<4}")
    print("  " + "-" * 78)


if __name__ == "__main__":
    _ensure_data_dir()
    print(f"Data directory ready : {DATA_DIR}/")
    print_saved_patients()
    print_saved_appointments()
    print_saved_bills()
