from patient import Patient
from doctor import (
    Doctor, Appointment,
    input_str, input_int, input_float, input_bool, input_date, input_time,
    calculate_appointment_cost,
)
from billing import HealthMetrics

import file_handler as fh


LINE = "═" * 64

session = {
    "patients_registered":  0,
    "doctors_registered":   0,
    "appointments_created": 0,
    "bills_created":        0,
    "total_revenue":        0.0,
}


def banner() -> None:
    print("\n" + LINE)
    print("   ★  SMART HOSPITAL MANAGEMENT SYSTEM  ★")
    print("       Team 9 - Advanced Python (PRG1406)")
    print(LINE)


def menu() -> str:
    print("\n" + "-" * 64)
    print("  MAIN MENU")
    print("-" * 64)
    print("   1.  Register a new patient")
    print("   2.  Manage doctors and appointments")
    print("   3.  Create a bill (consultation + medicine + insurance)")
    print("   4.  View saved patients")
    print("   5.  View saved appointments")
    print("   6.  View saved bills")
    print("   0.  Exit")
    print("-" * 64)
    return input("  Your choice : ").strip()


def handle_register_patient() -> None:
    print("\n" + "─" * 64)
    print("  REGISTER A NEW PATIENT")
    print("─" * 64)

    # Patient.from_input() casts to int/float but does not re-prompt,
    # so we catch and restart instead of crashing the menu.
    while True:
        try:
            patient = Patient.from_input()
            break
        except ValueError as e:
            print(f"  ⚠  Invalid input ({e}). Please start over.")

    print(patient)
    path = fh.save_patient(patient)
    print(f"\n  ✓ Patient saved to {path}")
    session["patients_registered"] += 1


def handle_doctors_and_appointments() -> None:
    print("\n" + "─" * 64)
    print("  DOCTORS AND APPOINTMENTS")
    print("─" * 64)

    doctors: list[Doctor] = []
    num_doctors = input_int(
        "  How many doctors do you want to register? (1-10) : ", 1, 10
    )

    for i in range(num_doctors):
        print(f"\n  -- Doctor {i + 1} / {num_doctors} --")
        staff_id = input_str(f"  ID (e.g. D{i + 1:03d}) : ")
        name     = input_str("  Full name : ")
        age      = input_int("  Age : ", 24, 80)

        while True:
            specialty = input_str(
                "  Specialty\n"
                "  (generaliste / cardiologie / pediatrie / chirurgie /\n"
                "   neurologie / dermatologie / gynecologie / ophtalmologie / urgences)\n"
                "  Your choice : "
            )
            if Doctor.is_valid_specialty(specialty):
                break
            print("  ⚠  Specialty not recognised, try again.")

        fee       = input_float("  Consultation fee (FCFA) : ")
        is_active = input_bool("  Is the doctor active? (oui/non) : ")

        doc = Doctor(
            staff_id=staff_id, name=name, age=age, is_active=is_active,
            specialty=specialty.strip().lower(), consultation_fee=fee,
        )
        doctors.append(doc)
        session["doctors_registered"] += 1
        print(f"  ✓ Registered : {doc.summary}")

    num_appts = input_int(
        "\n  How many appointments do you want to create? (0-20) : ", 0, 20
    )

    appt_counter = 0
    for j in range(num_appts):
        print(f"\n  -- Appointment {j + 1} / {num_appts} --")
        patient_name = input_str("  Patient name : ")
        date         = input_date("  Date (DD/MM/YYYY) : ")
        time         = input_time("  Time (HH:MM) : ")
        reason       = input_str("  Reason : ")
        is_urgent    = input_bool("  Urgent case? (oui/non) : ")

        print("\n  Available doctors :")
        for idx, d in enumerate(doctors):
            print(f"    {idx + 1}. {d.summary}")

        choice = input_int(
            f"  Assign to which doctor? (1-{len(doctors)}) : ", 1, len(doctors)
        )
        chosen = doctors[choice - 1]

        appt_counter += 1
        appt = Appointment(
            appointment_id=f"RDV{appt_counter:04d}",
            patient_name=patient_name, date=date, time=time,
            reason=reason, is_urgent=is_urgent,
        )
        chosen.assign_appointment(appt)
        session["appointments_created"] += 1

        cost = calculate_appointment_cost(chosen.consultation_fee, is_urgent, len(chosen))
        session["total_revenue"] += cost

        path = fh.save_appointment(chosen.name, appt)
        print(f"  ✓ Appointment {appt.appointment_id} created. "
              f"Estimated cost: {cost:,.0f} FCFA  →  saved to {path}")

    print("\n  " + "─" * 60)
    print(f"  Doctors registered    : {len(doctors)}")
    print(f"  Appointments created  : {appt_counter}")
    for d in doctors:
        d.display_appointments()


def handle_create_bill() -> None:
    print("\n" + "─" * 64)
    print("  NEW BILL (consultation + medicine + insurance + health)")
    print("─" * 64)

    record = HealthMetrics.from_input()
    record.print_summary()

    path = fh.save_bill(record)
    print(f"\n  ✓ Bill saved to {path}")
    print(f"  __str__ output : {record}")

    session["bills_created"] += 1
    session["total_revenue"] += record.total


def final_summary() -> None:
    print("\n" + LINE)
    print("   ★  SESSION SUMMARY  ★")
    print(LINE)
    print(f"   Patients registered    : {session['patients_registered']}")
    print(f"   Doctors registered     : {session['doctors_registered']}")
    print(f"   Appointments created   : {session['appointments_created']}")
    print(f"   Bills created          : {session['bills_created']}")
    print(f"   Estimated revenue      : {session['total_revenue']:,.0f} FCFA")
    print(LINE)

    all_patients     = len(fh.load_patients())
    all_appointments = len(fh.load_appointments())
    all_bills        = len(fh.load_bills())
    print(f"   Total saved on disk    :  {all_patients} patient(s),  "
          f"{all_appointments} appointment(s),  {all_bills} bill(s)")
    print(LINE)
    print("   Goodbye!\n")


def main() -> None:
    banner()

    handlers = {
        "1": handle_register_patient,
        "2": handle_doctors_and_appointments,
        "3": handle_create_bill,
        "4": fh.print_saved_patients,
        "5": fh.print_saved_appointments,
        "6": fh.print_saved_bills,
    }

    while True:
        choice = menu()

        if choice == "0":
            final_summary()
            break

        action = handlers.get(choice)
        if action is None:
            print("  ⚠  Invalid choice. Please pick 0-6.")
            continue

        try:
            action()
        except KeyboardInterrupt:
            print("\n  ⚠  Action cancelled.")
        except Exception as e:
            print(f"  ⚠  Something went wrong : {e}")


if __name__ == "__main__":
    main()
