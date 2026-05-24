# consultation.py
# Smart Hospital Management System
# -----------------------------------------------------------------
# Responsibility : Everything related to consultation fees.
# Used by        : billing.py (imports ConsultationRecord)
# -----------------------------------------------------------------

# ═══════════════════════════════════════════════════════════════════
#  UI HELPERS  —  reusable display functions for the console
# ═══════════════════════════════════════════════════════════════════

# Width of every box drawn in the console (keep consistent across files)
BOX_WIDTH = 54

def box_top(title: str = "") -> None:
    """Print the top border of a box, with an optional centred title."""
    if title:
        # Centre the title inside stars
        inner = f"  ★  {title}  ★  "
        pad   = (BOX_WIDTH - len(inner)) // 2
        print("*" * pad + inner + "*" * pad)
    else:
        print("*" * BOX_WIDTH)

def box_bottom() -> None:
    """Print the bottom border of a box."""
    print("*" * BOX_WIDTH)

def box_divider() -> None:
    """Print a thin divider line inside a box."""
    print("_" * BOX_WIDTH)

def box_row(label: str, value: str) -> None:
    """
    Print one labelled row inside a box.
    Example:  |  Consultation fee   :   5,000.00 FCFA      |
    """
    content = f"  {label:<22}: {value}"
    # Pad to keep the right edge aligned
    print(f"|{content:<{BOX_WIDTH - 2}}|")

def box_line(text: str = "") -> None:
    """Print a plain line of text inside a box (centred or left-aligned)."""
    print(f"|  {text:<{BOX_WIDTH - 4}}|")

def section_header(title: str) -> None:
    """
    Print a standalone section header between boxes.
    Example:  ___  CONSULTATION  ___
    """
    inner = f"  {title}  "
    pad   = (BOX_WIDTH - len(inner)) // 2
    print("\n" + "_" * pad + inner + "_" * pad)

def prompt_input(label: str) -> str:
    """
    Display a formatted input prompt.
    Example:  >>  Patient name : ___
    """
    return input(f"  >>  {label:<24}: ").strip()


# ═══════════════════════════════════════════════════════════════════
#  ConsultationRecord CLASS
# ═══════════════════════════════════════════════════════════════════

class ConsultationRecord:
    """
    Represents a single patient consultation.

    Stores the consultation type and computes the fee automatically
    based on class-level rate tables.

    Attributes:
        patient_name (str)  : full name of the patient
        consult_type (str)  : one of the keys in CONSULT_RATES
        doctor_name  (str)  : name of the attending doctor
        is_emergency (bool) : emergency visits carry an extra surcharge
    """

    # Consultation type → base fee in FCFA
    CONSULT_RATES: dict = {
        "general":    5_000,
        "specialist": 15_000,
        "emergency":  25_000,
        "follow-up":   3_000,
    }

    # Extra charge added on top when visit is flagged as emergency
    EMERGENCY_SURCHARGE: float = 0.30   # 30 %

    def __init__(
        self,
        patient_name: str,
        consult_type: str,
        doctor_name: str,
        is_emergency: bool = False,
    ) -> None:
        self.patient_name: str  = patient_name
        self.consult_type: str  = consult_type.lower()
        self.doctor_name: str   = doctor_name
        self.is_emergency: bool = is_emergency

    # ------------------------------------------------------------------
    # __str__ : one-line summary used by print()
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f"Consultation | {self.patient_name} | "
            f"{self.consult_type.capitalize()} | "
            f"{self.fee:,.0f} FCFA"
        )

    # ------------------------------------------------------------------
    # fee (property) : computes the final consultation fee.
    #   Base fee  →  looked up from CONSULT_RATES
    #   Surcharge →  added only when is_emergency is True
    # ------------------------------------------------------------------
    @property
    def fee(self) -> float:
        base: float = float(self.CONSULT_RATES.get(self.consult_type, 5_000))
        if self.is_emergency:
            return base + base * self.EMERGENCY_SURCHARGE
        return base

    # ------------------------------------------------------------------
    # @classmethod from_input() : interactive console constructor.
    # Collects data with a styled interface and full input validation.
    # ------------------------------------------------------------------
    @classmethod
    def from_input(cls) -> "ConsultationRecord":

        section_header("CONSULTATION DETAILS")
        box_top()

        # --- Patient name ---
        while True:
            name = prompt_input("Patient full name")
            if name:
                break
            box_line("  ⚠  Name cannot be empty.")
        box_divider()

        # --- Doctor name ---
        while True:
            doctor = prompt_input("Doctor name")
            if doctor:
                break
            box_line("  ⚠  Doctor name cannot be empty.")
        box_divider()

        # --- Consultation type: show a mini menu ---
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

        # --- Emergency flag (correct boolean pattern) ---
        is_emergency: bool = (
            prompt_input("Emergency visit? (yes/no)").lower() == "yes"
        )

        box_bottom()
        return cls(name, c_type, doctor, is_emergency)

    # ------------------------------------------------------------------
    # print_summary() : styled consultation summary box.
    # ------------------------------------------------------------------
    def print_summary(self) -> None:
        section_header("CONSULTATION SUMMARY")
        box_top()
        box_row("Patient",          self.patient_name)
        box_row("Doctor",           self.doctor_name)
        box_row("Type",             self.consult_type.capitalize())
        box_row("Emergency visit",  "Yes  ⚠" if self.is_emergency else "No")
        box_divider()

        if self.is_emergency:
            base = self.CONSULT_RATES[self.consult_type]
            box_row("Base fee",         f"{base:>10,} FCFA")
            box_row(f"Surcharge (+{int(self.EMERGENCY_SURCHARGE*100)}%)",
                    f"{base * self.EMERGENCY_SURCHARGE:>10,.0f} FCFA")
            box_divider()

        box_row("Consultation fee",  f"{self.fee:>10,.2f} FCFA")
        box_bottom()
