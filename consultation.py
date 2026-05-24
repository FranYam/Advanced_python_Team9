BOX_WIDTH = 54


def box_top(title: str = "") -> None:
    if title:
        inner = f"  ★  {title}  ★  "
        pad   = (BOX_WIDTH - len(inner)) // 2
        print("*" * pad + inner + "*" * pad)
    else:
        print("*" * BOX_WIDTH)


def box_bottom() -> None:
    print("*" * BOX_WIDTH)


def box_divider() -> None:
    print("_" * BOX_WIDTH)


def box_row(label: str, value: str) -> None:
    content = f"  {label:<22}: {value}"
    print(f"|{content:<{BOX_WIDTH - 2}}|")


def box_line(text: str = "") -> None:
    print(f"|  {text:<{BOX_WIDTH - 4}}|")


def section_header(title: str) -> None:
    inner = f"  {title}  "
    pad   = (BOX_WIDTH - len(inner)) // 2
    print("\n" + "_" * pad + inner + "_" * pad)


def prompt_input(label: str) -> str:
    return input(f"  >>  {label:<24}: ").strip()


class ConsultationRecord:

    CONSULT_RATES: dict = {
        "general":    5_000,
        "specialist": 15_000,
        "emergency":  25_000,
        "follow-up":   3_000,
    }

    EMERGENCY_SURCHARGE: float = 0.30

    def __init__(
        self,
        patient_name: str,
        consult_type: str,
        doctor_name: str,
        is_emergency: bool = False,
    ) -> None:
        self.patient_name = patient_name
        self.consult_type = consult_type.lower()
        self.doctor_name  = doctor_name
        self.is_emergency = is_emergency

    def __str__(self) -> str:
        return (
            f"Consultation | {self.patient_name} | "
            f"{self.consult_type.capitalize()} | "
            f"{self.fee:,.0f} FCFA"
        )

    @property
    def fee(self) -> float:
        base = float(self.CONSULT_RATES.get(self.consult_type, 5_000))
        if self.is_emergency:
            return base + base * self.EMERGENCY_SURCHARGE
        return base

    @classmethod
    def from_input(cls) -> "ConsultationRecord":
        section_header("CONSULTATION DETAILS")
        box_top()

        while True:
            name = prompt_input("Patient full name")
            if name:
                break
            box_line("  ⚠  Name cannot be empty.")
        box_divider()

        while True:
            doctor = prompt_input("Doctor name")
            if doctor:
                break
            box_line("  ⚠  Doctor name cannot be empty.")
        box_divider()

        box_line("  Available types:")
        for key, rate in cls.CONSULT_RATES.items():
            box_line(f"    [ {key:<10} ]  {rate:>8,} FCFA")
        box_divider()

        while True:
            c_type = prompt_input("Consultation type")
            if c_type.lower() in cls.CONSULT_RATES:
                c_type = c_type.lower()
                break
            box_line(f"  ⚠  Choose: {', '.join(cls.CONSULT_RATES.keys())}")
        box_divider()

        # Correct boolean pattern — never bool(input(...)).
        is_emergency = prompt_input("Emergency visit? (yes/no)").lower() == "yes"

        box_bottom()
        return cls(name, c_type, doctor, is_emergency)

    def print_summary(self) -> None:
        section_header("CONSULTATION SUMMARY")
        box_top()
        box_row("Patient",         self.patient_name)
        box_row("Doctor",          self.doctor_name)
        box_row("Type",            self.consult_type.capitalize())
        box_row("Emergency visit", "Yes  ⚠" if self.is_emergency else "No")
        box_divider()

        if self.is_emergency:
            base = self.CONSULT_RATES[self.consult_type]
            box_row("Base fee",     f"{base:>10,} FCFA")
            box_row(
                f"Surcharge (+{int(self.EMERGENCY_SURCHARGE*100)}%)",
                f"{base * self.EMERGENCY_SURCHARGE:>10,.0f} FCFA",
            )
            box_divider()

        box_row("Consultation fee", f"{self.fee:>10,.2f} FCFA")
        box_bottom()
