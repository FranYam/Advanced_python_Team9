from consultation import (
    BOX_WIDTH, box_top, box_bottom, box_divider,
    box_row, box_line, section_header, prompt_input,
)


class MedicineRecord:

    DISCOUNT_THRESHOLD: float = 20_000
    BULK_DISCOUNT_RATE: float = 0.10

    def __init__(self, patient_name: str) -> None:
        self.patient_name = patient_name
        self.medicines: list = []

    def __str__(self) -> str:
        return (
            f"Medicines | {self.patient_name} | "
            f"{len(self.medicines)} item(s) | "
            f"Net: {self.total_after_discount:,.2f} FCFA"
        )

    def __len__(self) -> int:
        return len(self.medicines)

    def add_medicine(self, name: str, unit_price: float, quantity: int) -> None:
        self.medicines.append({
            "name":       name.strip(),
            "unit_price": float(unit_price),
            "quantity":   int(quantity),
        })

    @property
    def gross_total(self) -> float:
        return sum(item["unit_price"] * item["quantity"] for item in self.medicines)

    @property
    def qualifies_for_bulk_discount(self) -> bool:
        return self.gross_total >= self.DISCOUNT_THRESHOLD

    @property
    def bulk_discount_amount(self) -> float:
        if self.qualifies_for_bulk_discount:
            return self.gross_total * self.BULK_DISCOUNT_RATE
        return 0.0

    @property
    def total_after_discount(self) -> float:
        return self.gross_total - self.bulk_discount_amount

    @staticmethod
    def format_line(name: str, unit_price: float, quantity: int) -> str:
        line_total = unit_price * quantity
        return f"  {name:<18} {unit_price:>8,.0f} x{quantity:<3}  = {line_total:>9,.0f} FCFA"

    @staticmethod
    def _prompt_number(label, parser, min_value, error_msg, indent="  "):
        while True:
            try:
                value = parser(prompt_input(label))
                if value < min_value:
                    raise ValueError(error_msg)
                return value
            except ValueError as e:
                box_line(f"{indent}⚠  {e}")

    @staticmethod
    def _prompt_non_empty(label, indent="  "):
        while True:
            value = prompt_input(label)
            if value:
                return value
            box_line(f"{indent}⚠  Cannot be empty.")

    @classmethod
    def _prompt_one_medicine(cls, index, total):
        box_line(f"  ★  Medicine {index} of {total}")
        box_divider()
        name  = cls._prompt_non_empty("  Name", indent="    ")
        price = cls._prompt_number("  Unit price (FCFA)", float, 0, "Price must be non-negative.", indent="    ")
        qty   = cls._prompt_number("  Quantity", int, 1, "Quantity must be at least 1.", indent="    ")
        return name, price, qty

    @classmethod
    def from_input(cls, patient_name: str) -> "MedicineRecord":
        record = cls(patient_name)

        section_header("MEDICINE ENTRY")
        box_top()

        count = cls._prompt_number(
            "Number of medicines", int, 0, "Must be 0 or more."
        )
        box_divider()

        for i in range(1, count + 1):
            name, price, qty = cls._prompt_one_medicine(i, count)
            record.add_medicine(name, price, qty)
            if i < count:
                box_divider()

        box_bottom()
        return record

    def print_summary(self) -> None:
        section_header("MEDICINE SUMMARY")
        box_top()

        box_line(f"  {'Medicine':<18} {'Unit':>8}  {'Qty':<5} {'Total':>12}")
        box_divider()

        for item in self.medicines:
            line = self.format_line(item["name"], item["unit_price"], item["quantity"])
            print(f"|{line:<{BOX_WIDTH - 2}}|")

        box_divider()
        box_row("Gross total", f"{self.gross_total:>10,.2f} FCFA")

        if self.qualifies_for_bulk_discount:
            box_row(
                f"Bulk discount (-{int(self.BULK_DISCOUNT_RATE * 100)}%)",
                f"-{self.bulk_discount_amount:>9,.2f} FCFA",
            )
        else:
            remaining = self.DISCOUNT_THRESHOLD - self.gross_total
            box_line(f"  (Add {remaining:,.0f} FCFA more to unlock 10% discount)")

        box_divider()
        box_row("Medicine total", f"{self.total_after_discount:>10,.2f} FCFA")
        box_bottom()
