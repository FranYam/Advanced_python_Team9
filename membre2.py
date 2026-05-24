class Person:
    def __init__(self, name, age, gender, phone):
        self.name   = name
        self.age    = age
        self.gender = gender
        self.phone  = phone

    def __str__(self):
        return f"Name: {self.name} | Age: {self.age} | Gender: {self.gender} | Phone: {self.phone}"


class Patient(Person):
    _counter = 1

    def __init__(self, name, age, gender, phone, temperature, pain_level, heart_rate, weight, height):
        super().__init__(name, age, gender, phone)
        self.temperature   = temperature
        self.pain_level    = pain_level
        self.heart_rate    = heart_rate
        self.weight        = weight
        self.height        = height
        self.patient_id    = f"PAT-{Patient._counter:04d}"
        Patient._counter  += 1
        self.urgency_score, self.urgency_label = self._calculate_urgency()

    def _calculate_urgency(self):
        score = 0

        # Age
        if self.age < 5 or self.age >= 75:    score += 3
        elif self.age < 12 or self.age >= 60: score += 2
        elif self.age < 18 or self.age >= 50: score += 1

        # Temperature
        if self.temperature >= 40.0:   score += 3
        elif self.temperature >= 38.5: score += 2
        elif self.temperature >= 37.5: score += 1

        # Pain level
        if self.pain_level >= 8:   score += 3
        elif self.pain_level >= 5: score += 2
        elif self.pain_level >= 3: score += 1

        # Heart rate
        if self.heart_rate > 130 or self.heart_rate < 45:   score += 3
        elif self.heart_rate > 110 or self.heart_rate < 55: score += 2
        elif self.heart_rate > 100 or self.heart_rate < 60: score += 1

        score = min(score, 10)
        if score >= 8:   label = " CRITICAL"
        elif score >= 5: label = " URGENT"
        elif score >= 3: label = " MODERATE"
        else:            label = " NON-URGENT"
        return score, label

    def __str__(self):
        return (
            f"\n=== PATIENT {self.patient_id} ===\n"
            f"{super().__str__()}\n"
            f"Temp: {self.temperature}°C | Pain: {self.pain_level}/10 | "
            f"Heart rate: {self.heart_rate}bpm | {self.weight}kg / {self.height}cm\n"
            f"Urgency: {self.urgency_label} (score {self.urgency_score}/10)"
        )

    def __repr__(self):
        return f"Patient({self.patient_id}, {self.name}, {self.urgency_label})"

    def __lt__(self, other):
        return self.urgency_score > other.urgency_score  # descending sort

    def to_record(self):
        return (f"{self.patient_id}|{self.name}|{self.age}|{self.gender}|{self.phone}|"
                f"{self.temperature}|{self.pain_level}|{self.heart_rate}|"
                f"{self.weight}|{self.height}|{self.urgency_score}|{self.urgency_label}\n")

    @classmethod
    def from_input(cls):
        print("\n=== REGISTER NEW PATIENT ===")
        name        = input("Full name         : ").strip()
        age         = int(input("Age               : "))
        gender      = input("Gender (M/F/Other) : ").strip()
        phone       = input("Phone             : ").strip()
        temperature = float(input("Temperature (°C)  : "))
        pain_level  = int(input("Pain level (0-10) : "))
        heart_rate  = int(input("Heart rate (bpm)  : "))
        weight      = float(input("Weight (kg)       : "))
        height      = float(input("Height (cm)       : "))
        return cls(name, age, gender, phone, temperature, pain_level, heart_rate, weight, height)