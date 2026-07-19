# Estimate cycle phase from period records alone (SFR-007)
# Without precise ovulation tracking, this uses the common clinical assumption that
# the luteal phase is a fixed ~14 days after ovulation.
from datetime import date

PHASE_ORDER = {"Menstrual": 0, "Follicular": 1, "Fertility": 2, "Luteal": 3}

LUTEAL_LENGTH = 14


def compute_phase(last_period_start: date, cycle_length: int, today: date, period_length: int = 5):
    cycle_length = max(cycle_length, period_length + 4)
    day_in_cycle = (today - last_period_start).days % cycle_length

    ovulation_day = max(cycle_length - LUTEAL_LENGTH, period_length + 1)
    fertile_start = ovulation_day - 2
    fertile_end = ovulation_day + 1

    if day_in_cycle < period_length:
        phase = "Menstrual"
    elif day_in_cycle < fertile_start:
        phase = "Follicular"
    elif day_in_cycle <= fertile_end:
        phase = "Fertility"
    else:
        phase = "Luteal"

    days_to_period = (cycle_length - day_in_cycle) % cycle_length
    return phase, days_to_period
