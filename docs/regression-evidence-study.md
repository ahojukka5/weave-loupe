# Historical compiler-regression evidence study

This repository owns the executable comparison for `ahojukka5/research#332`,
implemented under issue #100. The first study asks whether Loupe's retained
cross-stage evidence improves detection and localization of real historical
compiler regressions, and whether model review adds anything reliable after the
deterministic analysis has already run.

## Frozen evidence conditions

The first study has exactly five conditions:

1. `source-tests` — source change, relevant test result and ordinary logs;
2. `source-ir` — the same material plus conventionally inspectable WIR/LLVM;
3. `full-evidence` — every retained source-linked artifact available for that
   historical compiler state;
4. `deterministic` — full evidence plus the pre-existing Loupe deterministic
   analysis and contracts;
5. `deterministic-model` — identical deterministic evidence/status followed by
   one frozen model-review protocol.

The fifth condition is subordinate to the fourth: the model cannot change the
recorded deterministic gate status. A mismatch is rejected by the evidence
validator rather than counted as a model result.

## Freeze-before-score rule

`scripts/regression_evidence_protocol.py` defines the corpus and result contracts.
A frozen corpus records:

- one immutable Loupe revision;
- the compiler repository under study;
- one model/provider/configuration and review-prompt identity;
- the exact five evidence conditions above;
- each historical bad/good compiler revision pair;
- one independent oracle command for every defect;
- the expected first useful compilation stage;
- the known failure mechanism used only for scoring localization;
- the relevant regression tests.

The target is approximately 20 real historical defects. The validator requires
at least 10 qualified cases across at least four failure families. This lower
hard floor prevents filling the corpus with weak synthetic mutants solely to hit
a round target. If fewer than 10 real cases survive reconstruction, the parent
research protocol must be reconsidered before scoring.

A frozen corpus is content-addressed by `corpus_sha256`. Any later change to a
revision, oracle, mechanism, condition or model-review configuration invalidates
results from the prior corpus.

## Historical-case qualification

Prefer actual `weavec` defects for which a pre-fix state, fixing revision and
independent regression oracle can be reconstructed. Candidate families include:

- source formatter corruption;
- malformed or semantically invalid WIR lowering;
- call/cast/type lowering errors;
- missing diagnostics or protocol artifacts;
- build/cache publication failures;
- native/LLVM toolchain-boundary failures.

The corpus must not be chosen based on which evidence condition later detects a
defect. Freeze the cases before running the five-condition comparison. If modern
Loupe cannot materialize an artifact that the historical compiler never
published, record that evidence as unavailable rather than synthesizing it and
pretending it was contemporaneous.

Each admitted case keeps an independent executable oracle under
`experiments/compiler-evidence/oracles/`. The qualifier checks out the exact
bad and good SHAs, optionally builds that compiler, and runs the same oracle
command against both trees. A case whose defect is `scripts/build.sh` itself
sets `qualification.require_compiler_build` to `false`.

## Result contract

There is exactly one result row for every `(case, condition)` pair. The validator
rejects missing, duplicate or unknown rows. Every row records separately:

- defect detected;
- correct compilation phase localized;
- known failure mechanism localized/explained;
- false positive on the paired good revision;
- evidence bytes presented;
- model input/output tokens where applicable;
- review time;
- deterministic gate status for the two deterministic conditions.

Detection and localization are separate endpoints. A condition that notices a
failure but cannot identify the phase is not silently promoted to a localization
success.

## Information-budget discipline

Richer evidence arms naturally contain more bytes. The protocol therefore
records evidence volume and model tokens beside accuracy. A full-evidence win
cannot be interpreted as intrinsically better reasoning without acknowledging
that information advantage.

Likewise, model review is evaluated only after deterministic evidence exists. A
result in which deterministic checks are strong and the model adds no reliable
detections is scientifically valid.

## Scoring

The scorer reports, per condition:

- detection rate;
- phase-localization rate;
- mechanism-localization rate;
- false-positive rate;
- median evidence bytes;
- median model-token use where complete;
- median review time.

It separately reports whether model review adds, loses or preserves detections
relative to the deterministic condition. It does not combine detection,
localization, false positives and information cost into one weighted score.
Scientific interpretation belongs to the parent research report.

## Commands

Before replay/scoring:

```bash
python scripts/regression_evidence_protocol.py validate-corpus \
  experiments/compiler-evidence/corpus.json --require-frozen
```

During corpus construction:

```bash
python scripts/regression_evidence_protocol.py hash-corpus \
  experiments/compiler-evidence/corpus.json
```

Before freeze, qualify every historical pair with an independent oracle
that lives in this repository, not in the compiler revision under test:

```bash
python scripts/regression_evidence_qualify.py \
  experiments/compiler-evidence/corpus.json \
  --weavec-repo /path/to/weavec \
  --oracle-root . \
  --output build/regression-evidence/qualification.json
```

Admit a case only when the bad revision fails the oracle and the paired
good revision passes it. Do not freeze `corpus_sha256` until every
admitted case has that proof. Do not run model scoring against a draft
corpus.

After every condition is materialized and reviewed:

```bash
python scripts/regression_evidence_protocol.py score \
  experiments/compiler-evidence/corpus.json \
  experiments/compiler-evidence/results.json \
  --output experiments/compiler-evidence/score.json
```

## Interpretation boundary

This experiment evaluates the current evidence design. Do not add a new Loupe
rule after corpus freeze merely because a frozen defect is missed. A miss is a
result. New analyzers may be studied only after the parent research issue has
interpreted the first frozen comparison and authorized another experiment.
