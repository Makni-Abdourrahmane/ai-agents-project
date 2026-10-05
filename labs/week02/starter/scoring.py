"""The scorer. Two TODO markers, and it is the most important file today.

A prompt change is not an improvement until it has been measured, and this
is what measures it. Write it before you tune anything, because a scorer
written after you have seen the output tends to score what the output
already does.

One rule, and it decides most of the marks in this session: report per
field, as counts. Never one overall accuracy. Ten records means one error
moves a percentage by ten points, and an average across four fields hides
the only interesting thing in the data, which is that they do not move
together.
"""

from __future__ import annotations

from dataclasses import dataclass, field

FIELDS = ("category", "urgency", "due_date", "quote")


@dataclass
class FieldResult:
    correct: bool
    got: object
    expected: object
    note: str = ""


@dataclass
class Scoreboard:
    """Counts per field, plus the failures worth reading."""

    hits: dict[str, int] = field(
        default_factory=lambda: {f: 0 for f in FIELDS})
    total: int = 0
    invalid: int = 0
    failures: list[tuple[str, str, str]] = field(default_factory=list)

    def as_counts(self) -> str:
        return "  ".join(f"{f} {self.hits[f]:>2}/{self.total}"
                         for f in FIELDS)


# --------------------------------------------------------------------------
# TODO 3. Score one record against its gold annotation.
# --------------------------------------------------------------------------

def score_one(record, gold, document_text: str) -> dict[str, FieldResult]:
    results = {}
    ok = record.category == gold.category
    results["category"] = FieldResult(ok, record.category, gold.category,
                                      "" if ok else f"got {record.category!r}")
    
    ok = record.urgency == gold.urgency
    results["urgency"] = FieldResult(ok, record.urgency, gold.urgency,
                                     "" if ok else f"got {record.urgency!r}")

    got = record.due_date.isoformat() if record.due_date is not None else None
    ok =  got == gold.due_date
    results["due_date"] = FieldResult(ok, got, gold.due_date,
                                      "" if ok else f"got {got!r}, expected {gold.due_date!r}")

    ok =  record.quote != "" and record.quote in document_text
    results["quote"] = FieldResult(ok, record.quote, None,
                                   "" if ok else f"not verbatim: {record.quote!r}")

    return results


# --------------------------------------------------------------------------
# TODO 4. Aggregate.
# --------------------------------------------------------------------------

def score_all(records, golds, docs) -> Scoreboard:
    board = Scoreboard()

    for record, doc in zip(records, docs):
        board.total += 1

        if record is None:
            board.invalid += 1
            for f in FIELDS:
                board.failures.append((doc.id, f, "record failed validation"))
            continue

        results = score_one(record, golds[doc.id], doc.text)
        for f, res in results.items():
            if res.correct:
                board.hits[f] +=1
            else:
                board.failures.append((doc.id, f, res.note))

    return board


# --------------------------------------------------------------------------
# Given.
# --------------------------------------------------------------------------

def compare(a: Scoreboard, b: Scoreboard, label_a: str, label_b: str) -> str:
    """Two scoreboards side by side, per field, with the movement."""
    lines = [f"{'field':<10} {label_a:>12} {label_b:>12} {'move':>7}"]
    lines.append("-" * 44)
    for f in FIELDS:
        move = b.hits[f] - a.hits[f]
        lines.append(f"{f:<10} {a.hits[f]:>9}/{a.total} {b.hits[f]:>9}/{b.total} "
                     f"{move:>+7d}")
    lines.append(f"{'invalid':<10} {a.invalid:>12} {b.invalid:>12}")
    return "\n".join(lines)
