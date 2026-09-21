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
