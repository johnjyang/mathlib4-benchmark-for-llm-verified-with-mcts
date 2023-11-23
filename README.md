# mathlib4-benchmark-for-llm-verified-with-mcts

## Setup

Clone mathlib4 and json-gen4:

```
git clone https://github.com/johnjyang/json-gen4
git clone https://github.com/leanprover-community/mathlib4
```

add the following to `mathlib4/lakefile.lean`:

```
meta if get_config? env = some "dev" then
require «doc-gen4» from "../json-gen4"
```

run the following in `mathlib4` to build the jsonl files:

```
lake -R -Kenv=dev update
lake -R -Kenv=dev build Mathlib:docs
```
