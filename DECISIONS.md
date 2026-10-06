# Decisions

## Week 1

**Run conditions.** Everything below was produced on:

- machine: [AMD Ryzen 7 5700U (Radeon Graphics), 32GB RAM]
- model: [qwen3:4b-instruct]
- served by: Ollama, one request at a time, locally
- date: [2026-09-21]

Every number in this file is meaningless without those four lines, so they
are stated once here and referred to rather than repeated.

### 1. Machine and model set

I am running the [qwen3:4b-instruct, nomic-embed-text, qwen2.5:7b] model set.

I have not pulled the optional vision model yet. I will pull it before week 9.

### 2. The first call

| | |
| finish reason |stop|
| prompt tokens | 24|
| completion tokens | 45 |
| elapsed | 15.64s|

One sentence on the finish reason: if it gave me 'length' instead of 'stop' that means it got cut off while it was answering as it used all of its allowed tokens. The programm would then return finish_reason == "lenght"

[...]

### 3. Variance

| cell | distinct (recording) | distinct (mine) | median latency |
| closed_short, t=0.0 | 1/12 | | |
| closed_short, t=1.0 | 1/12 | | |

Which cell still returns a single answer at temperature 1.0, and why that
one:

[It is closed short, the question is 'what is the capital of luxembourg in one word' as there is only one answer. It is a closed ended question]

Which cells a test asserting exact string equality would pass on, and what
that tells me about testing this system:

[It would reliable pass for closed_short t00 and t01. It would reliably pass for open_short t00. Same thing for open_list t00 and open_reasoning t00. So basically every temperature 0 ones and temperature 1 for closed short. It would sometimes fail for the others. This tells us that we cannot test an AI the way we'd test a normal function as the output is changing. It does work for narrow cases (Temperatures at 0) but when we up the temperature it starts failing]

**The sentence that carries into week 10.** [The AI model is not random. It can repeat its exact wording if the temperature is at 0 and if the question is narrow ended and factual. If the temperature is higher or it is an open ended question.. We can get alot of variation in the answers nd therefore the testing methof has to be different.]

### 4. The cold start

- cold call: [ 9.4] s
- warm call: [ 0.49] s
- ratio: [ 19.1x]

What this implies for a system that uses more than one model, and what I
will do about it:

[My machine can only run one model at a time, if i load one it kicks the other out. This means that when it switches between models in a single request, we pay the 9s penalty for every switch. This is very slow. Its better to run all the steps that need one model together and then switch and run the other steps for the other model. This minimizes the cold start]

### 5. Cost, estimated

A 200-case golden set, at the token cost of my long case:

| | one run | nightly for the semester |
| small tier |0.03 EUR  |3.28 EUR |
| large tier | 2.49 EUR| 244.14 EUR|

Estimates against the price list dated [2026-08-10], not
measurements. Running locally, my actual monetary cost was zero.

Which tier I would run nightly, which I would run before a release, and why
not the same one for both:

[I would run the small tier nightly as its 3.28 for the whole semester and it is cheap enough to run every night. I would run the large tier before a release, while it costs much much much more, it reflects real production quality. Paying it once before shipping is worth, but paying it every night hurts my soul and my wallet as it would turn into around 244 EUR for a small value increase.]

### Deferred

[The homework for week 2.]

# Week 2: a structured-output extractor, measured

Copy this into your `DECISIONS.md` and fill it in.

---

## Week 2

**Run conditions.** model: [ qwen3:4b-instruct] | temperature: 0.0 | prompt version: [week02-zero-shot-v1 ] |
served locally | date: [2026-0929] | scored on: [my own machine (scorer developed on the recording)]

### 1. The output contract

The conventions I chose, and why:

- due_date, when the message states no date: ['null', the type is 'date | None' with no default, so the model must always write the field, and "" or "none" are rejected by validation. ]
- due_date, when the message states only a relative expression: [also 'null'. The model is told not to calculate or extrapolate a date from it. Dates written as DD/MM/YYYY are read as day first then month then year.]
- quote, and what "verbatim" means in my scorer: [correct only if the quote is not empty and appears exactly as is inside the original message.]
- what my scorer does with a record that failed validation: [counts it as 'invalid' and counts it wrong on all four fields. It stays in the total of 10. It is never skipped. ]

[A scorer that skips records it cannot parse reports a number that improves as the model gets worse: being invalid on 3 documents would score 7/7 instead of 7/10]

### 2. Zero-shot, per field

| field | correct | of |
| category |9 | 10 |
| urgency | 10 | 10 |
| due_date | 7 | 10 |
| quote | 7 | 10 |
| invalid records | 0 | 10 |

Failures:
- due_date, REQ-01, REQ-05, REQ-10: the model invented a date (2023-10-09,
2024-06-30, 2024-12-31) when the message only had a relative expression
like "before the end of the month". The correct answer was null.
- quote, REQ-01, REQ-04, REQ-07: the quotes were not exact copies.
REQ-01 copied from the start of the message, hit the max_length=200 limit
of the quote field and was cut off mid-word, ending in a garbage token.
REQ-04 and REQ-07 added "\n\n" at the end, which is not in the message.
In all three, the model picked a quote that was too long.
- category, REQ-08: a file server that stopped responding was labelled access
instead of hardware. The model read the symptom ("nobody can open a file")
as a permissions problem, instead of the cause (a broken server).

Tokens: 4183 over 10 calls, about 418 per call, about 418,000 per thousand
calls. 111.4 s for 10 documents.

My prediction, written before block 3: examples will help most on due_date
and quote. due_date, because an example where "next week" gives null shows
the model when it is not allowed to add a date, instead of only telling it.
quote, because examples with short quotes will make it copy shorter spans.
I do not expect category to improve, because no example is about a server,
so nothing shows that a broken server is hardware and not access.

### 3. Few-shot

Examples chosen, and the job each one does:

| example | why it is in the block | field it should move |
| | | |
| | | |
| | | |

| field | zero-shot | few-shot | move |
| category | | | |
| urgency | | | |
| due_date | | | |
| quote | | | |

### 4. What got worse

No field count went down, but one document did: REQ-05 quote was correct
zero-shot and wrong few-shot. The model wrote "ce n'est pas urgent..." but
the message says "Ce n'est pas urgent...". Only the capital C changed, and
the exact check catches it. My guess: my examples show short spans taken
from the middle of a message, so the model treated the quote as a fragment
and lowercased it. One document is not enough to prove this.

So the quote move of +2 is really 3 fixed (REQ-01, REQ-04, REQ-07, which were
too long or had "\n\n" added) and 1 newly broken (REQ-05).

due_date did not get fixed, it changed shape: the same three documents
(REQ-01, REQ-05, REQ-10) still have invented dates, just different ones
(e.g. REQ-01 2023-10-05 became 2024-09-03). Showing "next week" -> null in
an example did not stop the model calculating dates.

category REQ-08 (server labelled access) is unchanged, as predicted.

Also: zero-shot REQ-01 gave 2023-10-09 last week and 2023-10-05 this week,
with the same prompt at temperature 0. The local model is not perfectly
repeatable, which is another reason ten records are not enough to be sure.

### 5. What the examples cost

- extra input tokens per call: [ ]
- per thousand calls: [ ]
- estimated euros per thousand calls on the small tier: [ ], against the
  price list dated [ ]. Estimate, not a measurement.

### 6. Ship it or not

[Which variant, on what evidence, and what would change your mind. Ten
records is not enough to be confident and saying so is worth more than
claiming a win. If your answer is "keep one example and drop the rest", say
which one and why.]

### Sensitivity variant

Variant assigned: [ ]. What I changed: [ ]. What moved: [ ].

[If nothing moved, say so. A knob that changes nothing measurable is a real
result, and it tells the room which knobs are worth arguing about.]

### The gold set

Ten cases written to `artifacts/goldset.json`, tagged by language.

One thing my scorer cannot currently detect:

[This is the most valuable line on the page. An example: "our scorer cannot
tell a correctly formatted date that is simply the wrong date from a
correctly extracted one, because it only compares strings."]

### Deferred

[Anything you did not get to, and why.]
