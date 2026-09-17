"""Cycle-level calculations. Target eligibility is independent of baseline."""

from decimal import Decimal

from scripts.normalize import Row


def calculate(previous: str, current: str, target: str, direction: str, comparable: bool) -> Row:
    result: Row = dict(
        outcome_class="Insufficient data",
        performance_change="",
        performance_change_pct="",
        improvement_pct="",
        target_met="",
    )
    if not comparable or direction not in {"lower_is_better", "higher_is_better"}:
        return result
    if current == "":
        return result
    c = Decimal(current)
    sign = Decimal(-1 if direction == "lower_is_better" else 1)
    if target != "":
        result["target_met"] = str(sign * (c - Decimal(target)) >= 0).lower()
    if previous == "":
        return result
    b = Decimal(previous)
    delta = c - b
    result["performance_change"] = str(delta)
    result["outcome_class"] = "No material change" if delta == 0 else "Improved" if sign * delta > 0 else "Worsened"
    if b != 0:
        result["performance_change_pct"] = str(100 * delta / abs(b))
        result["improvement_pct"] = str(sign * 100 * delta / abs(b))
    return result
