class HospitalStaff:

    def __init__(self, staff_id: str, name: str, age: int, is_active: bool):
        self.staff_id  = staff_id
        self.name      = name
        self.age       = age
        self.is_active = is_active

    def __str__(self) -> str:
        status = "Actif" if self.is_active else "Inactif"
        return (
            f"[Staff #{self.staff_id}] {self.name} | "
            f"Age : {self.age} ans | Statut : {status}"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, HospitalStaff):
            return False
        return self.staff_id == other.staff_id


class Doctor(HospitalStaff):

    _doctor_count = 0

    def __init__(self, staff_id: str, name: str, age: int, is_active: bool,
                 specialty: str, consultation_fee: float):
        super().__init__(staff_id, name, age, is_active)
        self.specialty        = specialty
        self.consultation_fee = consultation_fee
        self.appointments     = []
        Doctor._doctor_count += 1

    def __str__(self) -> str:
        return (
            f"Dr. {self.name} (ID: {self.staff_id}) | "
            f"Specialite: {self.specialty} | "
            f"Honoraires: {self.consultation_fee:.2f} FCFA | "
            f"Rendez-vous: {len(self.appointments)}"
        )

    def __len__(self) -> int:
        return len(self.appointments)

    def assign_appointment(self, appointment) -> None:
        self.appointments.append(appointment)

    def display_appointments(self) -> None:
        if not self.appointments:
            print(f"  Aucun rendez-vous pour Dr. {self.name}.")
            return
        print(f"\n  Rendez-vous de Dr. {self.name}:")
        for i, appt in enumerate(self.appointments, start=1):
            print(f"    {i}. {appt}")
        print(f"  Total : {len(self.appointments)} rendez-vous")

    @classmethod
    def get_doctor_count(cls) -> int:
        return cls._doctor_count

    @staticmethod
    def is_valid_specialty(specialty: str) -> bool:
        valid = {
            "generaliste", "cardiologie", "pediatrie",
            "chirurgie", "neurologie", "dermatologie",
            "gynecologie", "ophtalmologie", "urgences",
        }
        return specialty.strip().lower() in valid

    @property
    def summary(self) -> str:
        active_str = "actif" if self.is_active else "inactif"
        return f"Dr. {self.name} - {self.specialty} ({active_str}, {len(self.appointments)} rdv)"


class Appointment:

    def __init__(self, appointment_id: str, patient_name: str, date: str,
                 time: str, reason: str, is_urgent: bool):
        self.appointment_id = appointment_id
        self.patient_name   = patient_name
        self.date           = date
        self.time           = time
        self.reason         = reason
        self.is_urgent      = is_urgent

    def __str__(self) -> str:
        urgency = "URGENT" if self.is_urgent else "Normal"
        return (
            f"[{self.appointment_id}] {self.patient_name} - "
            f"{self.date} a {self.time} | Motif: {self.reason} | {urgency}"
        )


def input_str(prompt: str) -> str:
    while True:
        try:
            value = input(prompt).strip()
            if not value:
                raise ValueError("Ce champ ne peut pas etre vide.")
            return value
        except ValueError as e:
            print(f"  Erreur : {e}")


def input_int(prompt: str, min_val: int = 0, max_val: int = 9999) -> int:
    while True:
        try:
            value = int(input(prompt).strip())
            if not (min_val <= value <= max_val):
                raise ValueError(f"Entrez un nombre entre {min_val} et {max_val}.")
            return value
        except ValueError as e:
            print(f"  Erreur : {e}")


def input_float(prompt: str, min_val: float = 0.0) -> float:
    while True:
        try:
            value = float(input(prompt).strip())
            if value < min_val:
                raise ValueError("La valeur doit etre positive.")
            return value
        except ValueError as e:
            print(f"  Erreur : {e}")


# Compare to "oui"/"non" — never use bool(input(...)) which is always True.
def input_bool(prompt: str) -> bool:
    while True:
        raw = input(prompt).strip().lower()
        if raw in ("oui", "o"):
            return True
        elif raw in ("non", "n"):
            return False
        else:
            print("  Erreur : tapez 'oui' ou 'non'.")


def input_date(prompt: str) -> str:
    while True:
        try:
            value = input(prompt).strip()
            parts = value.split("/")
            if len(parts) != 3 or not all(p.isdigit() for p in parts):
                raise ValueError("Format attendu : JJ/MM/AAAA")
            day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
            if not (1 <= day <= 31 and 1 <= month <= 12 and year >= 2024):
                raise ValueError("Date invalide.")
            return value
        except ValueError as e:
            print(f"  Erreur : {e}")


def input_time(prompt: str) -> str:
    while True:
        try:
            value = input(prompt).strip()
            parts = value.split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                raise ValueError("Format attendu : HH:MM")
            hour, minute = int(parts[0]), int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Heure invalide.")
            return value
        except ValueError as e:
            print(f"  Erreur : {e}")


def calculate_appointment_cost(base_fee: float, is_urgent: bool, num_appointments: int) -> float:
    urgent_surcharge   = base_fee * 0.5 if is_urgent else 0.0
    overload_surcharge = base_fee * 0.1 if num_appointments > 5 else 0.0
    return base_fee + urgent_surcharge + overload_surcharge


def doctor_utilization_rate(appointments: int, max_daily: int = 10) -> float:
    return (appointments / max_daily) * 100


def main():
    print("=" * 60)
    print("   SMART HOSPITAL - Gestion Medecins et Rendez-vous")
    print("=" * 60)

    doctors = []
    appointment_counter = 0

    print("\nETAPE 1 - Enregistrement des medecins\n")
    num_doctors = input_int("Combien de medecins voulez-vous enregistrer ? (1-10) : ", 1, 10)

    for i in range(num_doctors):
        print(f"\n  -- Medecin {i + 1} / {num_doctors} --")

        staff_id = input_str(f"  ID (ex: D{i+1:03d}) : ")
        name     = input_str("  Nom complet : ")
        age      = input_int("  Age : ", 24, 80)

        while True:
            specialty = input_str(
                "  Specialite\n"
                "  (generaliste / cardiologie / pediatrie / chirurgie /\n"
                "   neurologie / dermatologie / gynecologie / ophtalmologie / urgences)\n"
                "  Votre choix : "
            )
            if Doctor.is_valid_specialty(specialty):
                break
            print("  Specialite non reconnue, reessayez.")

        fee       = input_float("  Honoraires de consultation (FCFA) : ")
        is_active = input_bool("  Le medecin est-il actif ? (oui/non) : ")

        doc = Doctor(
            staff_id=staff_id, name=name, age=age, is_active=is_active,
            specialty=specialty.strip().lower(), consultation_fee=fee,
        )
        doctors.append(doc)
        print(f"\n  Medecin enregistre : {doc.summary}")

    print("\n" + "=" * 60)
    print("ETAPE 2 - Prise de rendez-vous\n")

    num_appts = input_int("Combien de rendez-vous voulez-vous creer ? (1-20) : ", 1, 20)

    for j in range(num_appts):
        print(f"\n  -- Rendez-vous {j + 1} / {num_appts} --")

        patient_name = input_str("  Nom du patient : ")
        date         = input_date("  Date (JJ/MM/AAAA) : ")
        time         = input_time("  Heure (HH:MM) : ")
        reason       = input_str("  Motif de la consultation : ")
        is_urgent    = input_bool("  Cas urgent ? (oui/non) : ")

        print("\n  Medecins disponibles :")
        for idx, d in enumerate(doctors):
            print(f"    {idx + 1}. {d.summary}")

        choice = input_int(
            f"  Assigner a quel medecin ? (1-{len(doctors)}) : ", 1, len(doctors)
        )
        chosen = doctors[choice - 1]

        appointment_counter += 1
        appt_id = f"RDV{appointment_counter:04d}"

        appt = Appointment(
            appointment_id=appt_id, patient_name=patient_name,
            date=date, time=time, reason=reason, is_urgent=is_urgent,
        )
        chosen.assign_appointment(appt)

        cost = calculate_appointment_cost(
            base_fee=chosen.consultation_fee,
            is_urgent=is_urgent,
            num_appointments=len(chosen),
        )
        print(f"\n  Rendez-vous {appt_id} cree. Cout estime : {cost:,.0f} FCFA")

    print("\n" + "=" * 60)
    print("RECAPITULATIF - Medecins et Rendez-vous")
    print("=" * 60)

    total_revenue = 0.0

    for doc in doctors:
        print(f"\n{doc}")
        doc.display_appointments()

        utilization = doctor_utilization_rate(len(doc))
        revenue = sum(
            calculate_appointment_cost(doc.consultation_fee, a.is_urgent, len(doc))
            for a in doc.appointments
        )
        total_revenue += revenue

        print(
            f"  Revenus estimes   : {revenue:,.0f} FCFA\n"
            f"  Taux d'occupation : {utilization:.1f}%"
        )

    print("\n" + "-" * 60)
    print(f"  Nombre de medecins    : {Doctor.get_doctor_count()}")
    print(f"  Nombre de rendez-vous : {appointment_counter}")
    print(f"  Revenus totaux        : {total_revenue:,.0f} FCFA")
    print("-" * 60)
    print("\n  Fin du programme.")
    print("=" * 60)


if __name__ == "__main__":
    main()
