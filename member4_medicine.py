# medicine.py
# Smart Hospital Management System
# -----------------------------------------------------------------
# Responsibility : Everything related to medicine fees.
#                 Applies an automatic bulk discount when the total
#                 medicine bill exceeds DISCOUNT_THRESHOLD.
# Used by        : billing.py (imports MedicineRecord)
# -----------------------------------------------------------------

# Import shared UI helpers from consultation.py
from consultation import (
    BOX_WIDTH, box_top, box_bottom, box_divider,
    box_row, box_line, section_header, prompt_input
)


# ═══════════════════════════════════════════════════════════════════
#  MedicineRecord CLASS
# ═══════════════════════════════════════════════════════════════════

class MedicineRecord:
    """
    Represents all medicines prescribed to a patient during a visit.

    Medicines are stored as a list of dicts with keys:
        'name', 'unit_price', 'quantity'

    A bulk discount is automatically applied when the gross total
    reaches or exceeds DISCOUNT_THRESHOLD.

    Attributes:
        patient_name (str)  : full name of the patient
        medicines    (list) : list of medicine dicts
    """

    # Minimum total to unlock the bulk discount
    DISCOUNT_THRESHOLD: float = 20_000   # 20 000 FCFA

    # Percentage taken off when the threshold is reached
    BULK_DISCOUNT_RATE: float = 0.10     # 10 %

    def __init__(self, patient_name: str) -> None:
        self.patient_name: str = patient_name
        self.medicines: list   = []       # starts empty; use add_medicine()

    # ------------------------------------------------------------------
    # __str__ : one-line summary used by print()
    # ------------------------------------------------------------------
    def __str__(self) -> str:
        return (
            f"Medicines | {self.patient_name} | "
            f"{len(self.medicines)} item(s) | "
            f"Net: {self.total_after_discount:,.2f} FCFA"
        )

    # ------------------------------------------------------------------
    # __len__ : returns the number of medicine items.
    # Allows:  len(medicine_record)
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self.medicines)

    # ------------------------------------------------------------------
    # add_medicine() : appends one medicine entry to the list.
    # ------------------------------------------------------------------
    def add_medicine(self, name: str, unit_price: float, quantity: int) -> None:
        self.medicines.append({
            "name":       name.strip(),
            "unit_price": float(unit_price),
            "quantity":   int(quantity),
        })

    # ------------------------------------------------------------------
    # gross_total (property) : sum of all lines before any discount.
    #   Each line = unit_price × quantity
    # ------------------------------------------------------------------
    @property
    def gross_total(self) -> float:
        return sum(
            item["unit_price"] * item["quantity"]
            for item in self.medicines
        )

    # ------------------------------------------------------------------
    # qualifies_for_bulk_discount (property) :
    #   True when gross_total >= DISCOUNT_THRESHOLD
    # ------------------------------------------------------------------
    @property
    def qualifies_for_bulk_discount(self) -> bool:
        return self.gross_total >= self.DISCOUNT_THRESHOLD

    # ------------------------------------------------------------------
    # bulk_discount_amount (property) : FCFA amount saved.
    #   Returns 0 when the patient does not qualify.
    # ------------------------------------------------------------------
    @property
    def bulk_discount_amount(self) -> float:
        if self.qualifies_for_bulk_discount:
            return self.gross_total * self.BULK_DISCOUNT_RATE
        return 0.0

    # ------------------------------------------------------------------
    # total_after_discount (property) : amount the patient pays for
    # medicines after the bulk discount is deducted.
    # ------------------------------------------------------------------
    @property
    def total_after_discount(self) -> float:
        return self.gross_total - self.bulk_discount_amount

    # ------------------------------------------------------------------
    # @staticmethod format_line() : formats one medicine row for display.
    # Static — doesn't need self or the class.
    # ------------------------------------------------------------------
    @staticmethod
    def format_line(name: str, unit_price: float, quantity: int) -> str:
        line_total = unit_price * quantity
        return f"  {name:<18} {unit_price:>8,.0f} x{quantity:<3}  = {line_total:>9,.0f} FCFA"

    # ------------------------------------------------------------------
    # @classmethod from_input() : interactive console constructor.
    # Asks how many medicines, then collects each one with validation.
    # ------------------------------------------------------------------
    @classmethod
    def from_input(cls, patient_name: str) -> "MedicineRecord":
        record = cls(patient_name)

        section_header("MEDICINE ENTRY")
        box_top()

        # --- Number of medicines ---
        while True:
            try:
                raw   = prompt_input("Number of medicines")
                count = int(raw)
                if count < 0:
                    raise ValueError("Must be 0 or more.")
                break
            except ValueError as e:
                box_line(f"  ⚠  {e}")
        box_divider()

        # --- Collect each medicine ---
        for i in range(1, count + 1):
            box_line(f"  ★  Medicine {i} of {count}")
            box_divider()

            # Name
            while True:
                name = prompt_input("  Name")
                if name:
                    break
                box_line("    ⚠  Name cannot be empty.")

            # Unit price
            while True:
                try:
                    price = float(prompt_input("  Unit price (FCFA)"))
                    if price < 0:
                        raise ValueError("Price must be non-negative.")
                    break
                except ValueError as e:
                    box_line(f"    ⚠  {e}")

            # Quantity
            while True:
                try:
                    qty = int(prompt_input("  Quantity"))
                    if qty <= 0:
                        raise ValueError("Quantity must be at least 1.")
                    break
                except ValueError as e:
                    box_line(f"    ⚠  {e}")

            record.add_medicine(name, price, qty)

            if i < count:
                box_divider()

        box_bottom()
        return record

    # ------------------------------------------------------------------
    # print_summary() : styled medicine bill breakdown box.
    # ------------------------------------------------------------------
    def print_summary(self) -> None:
        section_header("MEDICINE SUMMARY")
        box_top()

        # Column headers
        box_line(f"  {'Medicine':<18} {'Unit':>8}  {'Qty':<5} {'Total':>12}")
        box_divider()

        # One row per medicine
        for item in self.medicines:
            line = self.format_line(
                item["name"], item["unit_price"], item["quantity"]
            )
            print(f"|{line:<{BOX_WIDTH - 2}}|")

        box_divider()
        box_row("Gross total",   f"{self.gross_total:>10,.2f} FCFA")

        if self.qualifies_for_bulk_discount:
            box_row(
                f"Bulk discount (-{int(self.BULK_DISCOUNT_RATE * 100)}%)",
                f"-{self.bulk_discount_amount:>9,.2f} FCFA"
            )
        else:
            remaining = self.DISCOUNT_THRESHOLD - self.gross_total
            box_line(f"  (Add {remaining:,.0f} FCFA more to unlock 10% discount)")

        box_divider()
        box_row("Medicine total",  f"{self.total_after_discount:>10,.2f} FCFA")
        box_bottom()
