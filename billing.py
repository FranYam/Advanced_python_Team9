from consultation import (
    ConsultationRecord,
    box_top, box_bottom, box_divider,
    box_row, box_line, section_header, prompt_input, BOX_WIDTH,
)
from medicine import MedicineRecord


class Billing:
    """
    Aggregates a consultation + medicines into one bill.

    Discount order:
        1. Bulk medicine discount  (computed inside MedicineRecord)
        2. Insurance discount      (applied here on the subtotal)
        3. Tax                     (applied after insurance)
    """

    TAX_RATE: float               = 0.10
    DEFAULT_INSURANCE_RATE: float = 0.20

    def __init__(
        self,
        consultation: ConsultationRecord,
        medicine: MedicineRecord,
        has_insurance: bool,
        insurance_rate: float = DEFAULT_INSURANCE_RATE,
    ) -> None:
        self.consultation   = consultation
        self.medicine       = medicine
        self.has_insurance  = has_insurance
        self.insurance_rate = float(insurance_rate)

    def __str__(self) -> str:
        return (
            f"Bill | {self.consultation.patient_name} | "
            f"Subtotal: {self.subtotal:,.2f} FCFA | "
            f"Total due: {self.total:,.2f} FCFA"
        )

    @property
    def subtotal(self) -> float:
        return self.consultation.fee + self.medicine.total_after_discount

    @property
    def insurance_discount(self) -> float:
        if self.has_insurance:
            return self.subtotal * self.insurance_rate
        return 0.0

    @property
    def amount_after_insurance(self) -> float:
        return self.subtotal - self.insurance_discount

    @property
    def tax_amount(self) -> float:
        return self.amount_after_insurance * self.TAX_RATE

    @property
    def total(self) -> float:
        return self.amount_after_insurance + self.tax_amount

    @staticmethod
    def format_currency(amount: float) -> str:
        return f"{amount:,.2f} FCFA"

    @classmethod
    def from_input(cls) -> "Billing":
        consultation = ConsultationRecord.from_input()
        medicine     = MedicineRecord.from_input(consultation.patient_name)

        section_header("INSURANCE DETAILS")
        box_top()

        # Correct boolean pattern — never bool(input(...)).
        has_insurance = prompt_input("Has insurance? (yes/no)").lower() == "yes"

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
                    # Accept either "20" (percent) or "0.20" (decimal).
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

    def print_summary(self) -> None:
        self.consultation.print_summary()
        self.medicine.print_summary()

        section_header("FINAL BILL")
        box_top("HOSPITAL RECEIPT")
        box_row("Patient", self.consultation.patient_name)
        box_row("Doctor",  self.consultation.doctor_name)
        box_divider()
        box_row("Consultation fee", f"{self.format_currency(self.consultation.fee):>18}")
        box_row("Medicine (net)",   f"{self.format_currency(self.medicine.total_after_discount):>18}")
        box_divider()
        box_row("Subtotal",         f"{self.format_currency(self.subtotal):>18}")
        box_divider()

        if self.has_insurance:
            box_row(
                f"Insurance (-{int(self.insurance_rate * 100)}%)",
                f"-{self.format_currency(self.insurance_discount):>17}",
            )
        else:
            box_row("Insurance", "None")

        box_row(
            f"Tax (+{int(self.TAX_RATE * 100)}%)",
            f"+{self.format_currency(self.tax_amount):>17}",
        )
        box_divider()

        total_str = f"★  {self.format_currency(self.total)}  ★"
        pad = (BOX_WIDTH - len(total_str) - 4) // 2
        print(f"|{'':>{pad}}  {total_str}{'':>{BOX_WIDTH - len(total_str) - pad - 4}}  |")

        box_bottom()


class HealthMetrics(Billing):
    """Billing + physical measurements (weight, height, vitals) and BMI."""

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
        super().__init__(consultation, medicine, has_insurance, insurance_rate)
        self.weight_kg   = float(weight_kg)
        self.height_m    = float(height_m)
        self.temperature = float(temperature)
        self.heart_rate  = int(heart_rate)
        self.pain_level  = int(pain_level)

    def __str__(self) -> str:
        return f"{super().__str__()} | BMI: {self.bmi:.1f} ({self.bmi_category})"

    @property
    def bmi(self) -> float:
        if self.height_m <= 0:
            raise ValueError("Height must be greater than 0.")
        return self.weight_kg / (self.height_m ** 2)

    @property
    def bmi_category(self) -> str:
        b = self.bmi
        if b < 18.5:   return "Underweight"
        elif b < 25.0: return "Normal weight"
        elif b < 30.0: return "Overweight"
        else:          return "Obese"

    @property
    def is_fever(self) -> bool:
        return self.temperature > 37.5

    @property
    def is_tachycardia(self) -> bool:
        return self.heart_rate > 100

    @staticmethod
    def _prompt_range(label, parser, low, high, error_msg):
        while True:
            try:
                value = parser(prompt_input(label))
                if not (low <= value <= high):
                    raise ValueError(error_msg)
                return value
            except ValueError as e:
                box_line(f"  ⚠  {e}")

    @classmethod
    def from_input(cls) -> "HealthMetrics":
        billing = Billing.from_input()

        section_header("HEALTH METRICS")
        box_top()

        weight = cls._prompt_range("Weight (kg)", float, 0.1, 500.0, "Expected 0.1–500 kg.")
        box_divider()
        height = cls._prompt_range("Height (m)  e.g. 1.75", float, 0.1, 3.0, "Expected 0.1–3.0 m.")
        box_divider()
        temp   = cls._prompt_range("Temperature (°C)", float, 30.0, 45.0, "Expected 30–45 °C.")
        box_divider()
        hr     = cls._prompt_range("Heart rate (bpm)", int, 30, 300, "Expected 30–300 bpm.")
        box_divider()
        pain   = cls._prompt_range("Pain level (0 none → 10 worst)", int, 0, 10, "Must be between 0 and 10.")

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

    def print_summary(self) -> None:
        super().print_summary()

        section_header("HEALTH METRICS SUMMARY")
        box_top()
        box_row("Weight", f"{self.weight_kg:.1f} kg")
        box_row("Height", f"{self.height_m:.2f} m")
        box_divider()
        box_row("BMI",    f"{self.bmi:.1f}  →  {self.bmi_category}")
        box_divider()
        box_row("Temperature", f"{self.temperature:.1f} °C  {'⚠  FEVER' if self.is_fever else '✓  Normal'}")
        box_row("Heart rate",  f"{self.heart_rate} bpm  {'⚠  HIGH' if self.is_tachycardia else '✓  Normal'}")
        box_row("Pain level",  f"{self.pain_level} / 10")
        box_bottom()


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
