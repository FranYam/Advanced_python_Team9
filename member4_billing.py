# billing.py
# Smart Hospital Management System
# -----------------------------------------------------------------
# Responsibility : Combines ConsultationRecord + MedicineRecord,
#                 applies insurance discount on the combined total,
#                 adds tax, and produces the final bill.
#
# Imports        : ConsultationRecord  (consultation.py)
#                  MedicineRecord      (medicine.py)
# Used by        : main.py
# -----------------------------------------------------------------

from consultation import (
    ConsultationRecord,
    box_top, box_bottom, box_divider,
    box_row, box_line, section_header, prompt_input, BOX_WIDTH
)
from medicine import MedicineRecord


# ═══════════════════════════════════════════════════════════════════
#  Billing CLASS
# ═══════════════════════════════════════════════════════════════════

class Billing:
    """
    Aggregates a ConsultationRecord and a MedicineRecord into one bill.

    Discount order:
        1. Bulk medicine discount  (inside MedicineRecord)
        2. Insurance discount      (applied here on the combined subtotal)
        3. Tax                     (applied after insurance)

    Attributes:
        consultation  (ConsultationRecord) : the patient's consultation
        medicine      (MedicineRecord)     : the patient's medicines
        has_insurance (bool)               : whether the patient is insured
        insurance_rate(float)              : insurance discount rate (0.0–1.0)
    """

    TAX_RATE: float             = 0.10   # 10 % tax
    DEFAULT_INSURANCE_RATE: float = 0.20  # 20 % insurance discount

    def __init__(
        self,
        consultation: ConsultationRecord,
        medicine: MedicineRecord,
        has_insurance: bool,
        insurance_rate: float = DEFAULT_INSURANCE_RATE,
    ) -> None:
        self.consultation: ConsultationRecord = consultation
        self.medicine: MedicineRecord         = medicine
        self.has_insurance: bool              = has_insurance
        self.insurance_rate: float            = float(insurance_rate)

    # ------------------------------------------------------------------
    # __str__ : one-line summary used by print()
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f"Bill | {self.consultation.patient_name} | "
            f"Subtotal: {self.subtotal:,.2f} FCFA | "
            f"Total due: {self.total:,.2f} FCFA"
        )

    # ------------------------------------------------------------------
    # subtotal (property) : consultation fee + medicine net total.
    # Medicine bulk discount is already baked into total_after_discount.
    # ------------------------------------------------------------------
    @property
    def subtotal(self) -> float:
        return self.consultation.fee + self.medicine.total_after_discount

    # ------------------------------------------------------------------
    # insurance_discount (property) : FCFA saved with insurance.
    # Returns 0 when the patient is not insured.
    # ------------------------------------------------------------------
    @property
    def insurance_discount(self) -> float:
        if self.has_insurance:
            return self.subtotal * self.insurance_rate
        return 0.0

    # ------------------------------------------------------------------
    # amount_after_insurance (property) : base for tax calculation.
    # ------------------------------------------------------------------
    @property
    def amount_after_insurance(self) -> float:
        return self.subtotal - self.insurance_discount

    # ------------------------------------------------------------------
    # tax_amount (property) : tax applied after insurance discount.
    # ------------------------------------------------------------------
    @property
    def tax_amount(self) -> float:
        return self.amount_after_insurance * self.TAX_RATE

    # ------------------------------------------------------------------
    # total (property) : final amount the patient must pay.
    #   Formula: (subtotal − insurance_discount) + tax
    # ------------------------------------------------------------------
    @property
    def total(self) -> float:
        return self.amount_after_insurance + self.tax_amount

    # ------------------------------------------------------------------
    # @staticmethod format_currency() : formats any float as FCFA.
    # ------------------------------------------------------------------
    @staticmethod
    def format_currency(amount: float) -> str:
        return f"{amount:,.2f} FCFA"

    # ------------------------------------------------------------------
    # @classmethod from_input() : full interactive constructor.
    #
    # Order:
    #   1. ConsultationRecord.from_input()
    #   2. MedicineRecord.from_input()
    #   3. Insurance details (collected here)
    # ------------------------------------------------------------------
    @classmethod
    def from_input(cls) -> "Billing":

        # Step 1 — consultation
        consultation = ConsultationRecord.from_input()

        # Step 2 — medicines
        medicine = MedicineRecord.from_input(consultation.patient_name)

        # Step 3 — insurance
        section_header("INSURANCE DETAILS")
        box_top()

        # Correct boolean pattern: compare string, never cast input()
        has_insurance: bool = (
            prompt_input("Has insurance? (yes/no)").lower() == "yes"
        )

        insurance_rate = cls.DEFAULT_INSURANCE_RATE

        if has_insurance:
            box_divider()
            while True:
                try:
                    raw = prompt_input(
                        f"Discount rate (default {int(cls.DEFAULT_INSURANCE_RATE * 100)}%, Enter to keep)"
                    )
                    if raw == "":
                        break
                    rate = float(raw)
                    # Accept percentage entry (e.g. 20) or decimal (e.g. 0.20)
                    if 1.0 < rate <= 100.0:
                        rate /= 100.0
                    if not (0.0 <= rate <= 1.0):
                        raise ValueError("Rate must be between 0 and 100.")
                    insurance_rate = rate
                    break
                except ValueError as e:
                    box_line(f"  ⚠  {e}")

        box_bottom()
        return cls(consultation, medicine, has_insurance, insurance_rate)

    # ------------------------------------------------------------------
    # print_summary() : prints the full combined final bill box.
    # ------------------------------------------------------------------
    def print_summary(self) -> None:
        # Sub-summaries from each module
        self.consultation.print_summary()
        self.medicine.print_summary()

        # ── Final combined bill ────────────────────────────────────────
        section_header("FINAL BILL")
        box_top("HOSPITAL RECEIPT")
        box_row("Patient",            self.consultation.patient_name)
        box_row("Doctor",             self.consultation.doctor_name)
        box_divider()
        box_row("Consultation fee",   f"{self.format_currency(self.consultation.fee):>18}")
        box_row("Medicine (net)",     f"{self.format_currency(self.medicine.total_after_discount):>18}")
        box_divider()
        box_row("Subtotal",           f"{self.format_currency(self.subtotal):>18}")
        box_divider()

        if self.has_insurance:
            box_row(
                f"Insurance (-{int(self.insurance_rate * 100)}%)",
                f"-{self.format_currency(self.insurance_discount):>17}"
            )
        else:
            box_row("Insurance",      "None")

        box_row(
            f"Tax (+{int(self.TAX_RATE * 100)}%)",
            f"+{self.format_currency(self.tax_amount):>17}"
        )
        box_divider()

        # Total line — make it stand out
        total_str = f"★  {self.format_currency(self.total)}  ★"
        pad = (BOX_WIDTH - len(total_str) - 4) // 2
        print(f"|{'':>{pad}}  {total_str}{'':>{BOX_WIDTH - len(total_str) - pad - 4}}  |")

        box_bottom()


# ═══════════════════════════════════════════════════════════════════
#  HealthMetrics CLASS  —  child of Billing
# ═══════════════════════════════════════════════════════════════════

class HealthMetrics(Billing):
    """
    Extends Billing with patient physical measurements and vital signs.

    IS-A relationship: HealthMetrics IS a Billing.
    Everything Billing can do, HealthMetrics can do too — plus health data.

    Additional attributes:
        weight_kg   (float) : weight in kilograms
        height_m    (float) : height in metres
        temperature (float) : body temperature in °C
        heart_rate  (int)   : heart rate in beats per minute
        pain_level  (int)   : self-reported pain score 0–10
    """

    def __init__(
        self,
        consultation: ConsultationRecord,
        medicine: MedicineRecord,
        has_insurance: bool,
        weight_kg: float,
        height_m: float,
        temperature: float,
        heart_rate: int,
        pain_level: int,
        insurance_rate: float = Billing.DEFAULT_INSURANCE_RATE,
    ) -> None:
        # Initialise the Billing (parent) part first
        super().__init__(consultation, medicine, has_insurance, insurance_rate)

        # Attributes added by HealthMetrics
        self.weight_kg: float   = float(weight_kg)
        self.height_m: float    = float(height_m)
        self.temperature: float = float(temperature)
        self.heart_rate: int    = int(heart_rate)
        self.pain_level: int    = int(pain_level)

    # ------------------------------------------------------------------
    # __str__ : extends the parent summary with BMI info
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return f"{super().__str__()} | BMI: {self.bmi:.1f} ({self.bmi_category})"

    # ------------------------------------------------------------------
    # bmi (property) : Body Mass Index = weight(kg) / height(m)²
    # This is the @property required by the assignment for BMI.
    # ------------------------------------------------------------------
    @property
    def bmi(self) -> float:
        if self.height_m <= 0:
            raise ValueError("Height must be greater than 0.")
        return self.weight_kg / (self.height_m ** 2)

    # ------------------------------------------------------------------
    # bmi_category (property) : WHO BMI classification string.
    # ------------------------------------------------------------------
    @property
    def bmi_category(self) -> str:
        b = self.bmi
        if b < 18.5:  return "Underweight"
        elif b < 25.0: return "Normal weight"
        elif b < 30.0: return "Overweight"
        else:          return "Obese"

    # ------------------------------------------------------------------
    # is_fever (property) : True when temperature > 37.5 °C
    # ------------------------------------------------------------------
    @property
    def is_fever(self) -> bool:
        return self.temperature > 37.5

    # ------------------------------------------------------------------
    # is_tachycardia (property) : True when heart rate > 100 bpm
    # ------------------------------------------------------------------
    @property
    def is_tachycardia(self) -> bool:
        return self.heart_rate > 100

    # ------------------------------------------------------------------
    # @classmethod from_input() : collects billing + health data.
    # Reuses Billing.from_input() then adds the health metric inputs.
    # ------------------------------------------------------------------
    @classmethod
    def from_input(cls) -> "HealthMetrics":
        billing = Billing.from_input()

        section_header("HEALTH METRICS")
        box_top()

        # --- Weight ---
        while True:
            try:
                weight = float(prompt_input("Weight (kg)"))
                if weight <= 0: raise ValueError("Must be positive.")
                break
            except ValueError as e:
                box_line(f"  ⚠  {e}")
        box_divider()

        # --- Height ---
        while True:
            try:
                height = float(prompt_input("Height (m)  e.g. 1.75"))
                if height <= 0: raise ValueError("Must be positive.")
                break
            except ValueError as e:
                box_line(f"  ⚠  {e}")
        box_divider()

        # --- Temperature ---
        while True:
            try:
                temp = float(prompt_input("Temperature (°C)"))
                if not (30.0 <= temp <= 45.0):
                    raise ValueError("Expected 30–45 °C.")
                break
            except ValueError as e:
                box_line(f"  ⚠  {e}")
        box_divider()

        # --- Heart rate ---
        while True:
            try:
                hr = int(prompt_input("Heart rate (bpm)"))
                if not (30 <= hr <= 300):
                    raise ValueError("Expected 30–300 bpm.")
                break
            except ValueError as e:
                box_line(f"  ⚠  {e}")
        box_divider()

        # --- Pain level ---
        while True:
            try:
                pain = int(prompt_input("Pain level (0 none → 10 worst)"))
                if not (0 <= pain <= 10):
                    raise ValueError("Must be between 0 and 10.")
                break
            except ValueError as e:
                box_line(f"  ⚠  {e}")

        box_bottom()

        return cls(
            consultation   = billing.consultation,
            medicine       = billing.medicine,
            has_insurance  = billing.has_insurance,
            weight_kg      = weight,
            height_m       = height,
            temperature    = temp,
            heart_rate     = hr,
            pain_level     = pain,
            insurance_rate = billing.insurance_rate,
        )

    # ------------------------------------------------------------------
    # print_summary() : full bill + health metrics boxes.
    # ------------------------------------------------------------------
    def print_summary(self) -> None:
        # Parent prints: consultation summary, medicine summary, final bill
        super().print_summary()

        # Health metrics box
        section_header("HEALTH METRICS SUMMARY")
        box_top()
        box_row("Weight",       f"{self.weight_kg:.1f} kg")
        box_row("Height",       f"{self.height_m:.2f} m")
        box_divider()
        box_row("BMI",          f"{self.bmi:.1f}  →  {self.bmi_category}")
        box_divider()
        box_row("Temperature",  f"{self.temperature:.1f} °C  {'⚠  FEVER' if self.is_fever else '✓  Normal'}")
        box_row("Heart rate",   f"{self.heart_rate} bpm  {'⚠  HIGH' if self.is_tachycardia else '✓  Normal'}")
        box_row("Pain level",   f"{self.pain_level} / 10")
        box_bottom()


# ═══════════════════════════════════════════════════════════════════
#  Standalone demo — only runs when billing.py is executed directly.
#  In the full project, main.py imports and calls HealthMetrics.
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "★" * 54)
    print("★" + " SMART HOSPITAL MANAGEMENT SYSTEM ".center(52) + "★")
    print("★" + "    Billing & Health Calculations   ".center(52) + "★")
    print("★" * 54)

    record = HealthMetrics.from_input()
    record.print_summary()

    print("\n" + "_" * 54)
    print("  __str__ output:")
    print(f"  {record}")
    print("_" * 54)
