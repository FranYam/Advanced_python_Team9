# Smart Hospital Management System

A console program that runs a small hospital workflow end-to-end:
register patients, manage doctors and their appointments, produce a
bill for a visit (consultation + medicines + insurance + tax), and
compute basic health metrics (BMI, fever, tachycardia). All records
are persisted to plain text files in `data/`.

## How to run

Requires Python 3.9+. No third-party libraries.

```bash
python3 main.py
```

The first run creates a `data/` folder where patients, appointments
and bills are appended as text. Each module can also be run on its
own (`python3 billing.py`, `python3 doctor.py`, etc.).

The menu:

```
1.  Register a new patient
2.  Manage doctors and appointments
3.  Create a bill (consultation + medicine + insurance)
4.  View saved patients
5.  View saved appointments
6.  View saved bills
0.  Exit
```

## Classes

- **`Person`** → **`Patient`** *(patient.py)* — `Person` holds name,
  age, gender, phone. `Patient` adds vitals (temperature, pain,
  heart rate, weight, height), an auto-generated `PAT-NNNN` id, and
  an urgency score/label.

- **`HospitalStaff`** → **`Doctor`** *(doctor.py)* — `HospitalStaff`
  holds id, name, age, active flag. `Doctor` adds specialty,
  consultation fee, and a list of appointments. `Appointment` is a
  separate small class for one booking (id, patient, date, time,
  reason, urgent flag).

- **`ConsultationRecord`** *(consultation.py)* — one consultation;
  computes the fee from a rate table and applies an emergency
  surcharge when needed.

- **`MedicineRecord`** *(medicine.py)* — a list of prescribed
  medicines; computes a gross total and applies a bulk discount when
  the threshold is reached.

- **`Billing`** → **`HealthMetrics`** *(billing.py)* — `Billing`
  aggregates a `ConsultationRecord` and a `MedicineRecord`, applies
  insurance discount and tax, and prints the final receipt.
  `HealthMetrics` adds weight, height and vitals, and exposes `bmi`
  and `bmi_category`.

- **`file_handler`** *(file_handler.py)* — module (no class) that
  saves and reads records to `data/patients.txt`,
  `data/appointments.txt` and `data/bills.txt`.

- **`main`** *(main.py)* — the menu loop that wires everything
  together and prints a session summary at exit.
