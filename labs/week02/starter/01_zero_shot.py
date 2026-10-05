"""Block 2. The zero-shot baseline, scored per field.

    python 01_zero_shot.py --replay     # the shipped recording, instant
    python 01_zero_shot.py              # your own model, about 45 seconds

Develop your scorer against `--replay`. The recording holds every model
answer for both variants, so your scorer runs in well under a second and you
can iterate on it properly instead of waiting forty-five seconds to find out
you compared the wrong field.

The recording contains real failures, because the model really does make
them. If your scorer reports forty out of forty, your scorer does nothing.

One TODO marker here. TODO 1 to 4 live in extractor.py and scoring.py, and
this file will not run until they are done.
"""


from __future__ import annotations

import argparse
from dataclasses import asdict

from documents import DOCS, GOLD
from extractor import (PROMPT_VERSION, SYSTEM_ZERO_SHOT, get_client,
                       run_variant)
from project.contracts import GoldCase, GoldSet
from project.trace import write_json

EXPECTED_BEHAVIOR = {
    "REQ-01": "Extracts category access and urgency urgent, because the sender "
              "cannot sign in and needs a letter before an appointment tomorrow; "
              "due_date is null because 'tomorrow' and 'today' are relative, "
              "not calendar dates.",
    "REQ-02": "Extracts category hardware (a broken printer) and urgency "
              "standard; due_date is 2026-09-15, read day-first from "
              "'15/09/2026'; the quote stays in French.",
    "REQ-03": "Extracts category billing and urgency standard, because the "
              "sender asks for a correction but says 'Es eilt nicht'; due_date "
              "is null because no date is stated; the quote stays in German.",
    "REQ-04": "Extracts category facilities (a door that does not lock) and "
              "urgency urgent, because the building is open to anyone right "
              "now; due_date is null because 'immediately' is not a date.",
    "REQ-05": "Extracts category access (a new account and folder permissions) "
              "and urgency standard; due_date is null because 'avant la fin du "
              "mois' is relative and must not be turned into a date.",
    "REQ-06": "Extracts category billing (a supplier reference change) and "
              "urgency info, because the sender says no action is needed; "
              "due_date is null.",
    "REQ-07": "Extracts category facilities (broken heating) and urgency "
              "standard; due_date is 2026-10-01, from the German month name "
              "'1. Oktober 2026'; the quote stays in German.",
    "REQ-08": "Extracts category hardware, because the file server is down "
              "(not access: nobody is denied permission), and urgency urgent, "
              "because the whole team is blocked today; due_date is null.",
    "REQ-09": "Extracts category other (a suggestion) and urgency info, "
              "because the sender says it is just a suggestion; due_date is null.",
    "REQ-10": "Extracts category access (a shared mailbox) and urgency "
              "standard; due_date is null because 'before the end of the "
              "month' is relative and must not become a computed date.",
}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", action="store_true")
    args = ap.parse_args()

    client = get_client(args.replay)
    board, records, metas = run_variant(client, SYSTEM_ZERO_SHOT,
                                        "zero-shot", DOCS, GOLD)

    if board.failures:
        print("failures worth reading:")
        for doc_id, fieldname, note in board.failures[:10]:
            print(f"  {doc_id}  {fieldname:<9} {note}")

    write_json("artifacts/week02_zero_shot.json", {
        "variant": "zero-shot",
        "prompt_version": PROMPT_VERSION,
        "hits": board.hits, "total": board.total, "invalid": board.invalid,
    })

    # TODO 7. Write the gold set into the project spine.
    #
    #   Build a GoldSet out of the ten documents and their annotations and
    #   write it to artifacts/goldset.json with
    #   project.trace.write_json(...).
    #
    #   For each document, one GoldCase with:
    #     case_id           the document id
    #     week_added        2
    #     question          the document text
    #     expected          the gold annotation, as a dict
    #     expected_behavior one sentence a colleague could grade against.
    #                       "extracts category access and urgency standard,
    #                       with no due date because the message only says
    #                       'before the end of the month'" is a good one.
    #                       "works" is not.
    #     slice_tags        at least the language, so week 10 can report per
    #                       language instead of as one average
    #
    #   This is not busywork and it is not for today. Week 3 adds route
    #   labels to this file, week 7 adds retrieval questions, and week 10
    #   builds the evaluation harness on whatever is in it by then. Ten
    #   careful cases now is the cheapest week 10 you will ever have.
    #
    #   Then run: python -m project.verify

    cases = []
    for doc in DOCS:
        cases.append(GoldCase(
            case_id=doc.id,
            week_added=2,
            question=doc.text,
            expected=asdict(GOLD[doc.id]),       # turns the Gold object into a dict
            expected_behavior=EXPECTED_BEHAVIOR[doc.id],
            slice_tags=[f"lang:{doc.lang}"],     # e.g. "lang:fr"
        ))
    write_json("artifacts/goldset.json", GoldSet(cases=cases).model_dump(mode="json"))
    print(f"wrote artifacts/goldset.json ({len(cases)} cases)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
