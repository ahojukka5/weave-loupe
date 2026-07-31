# Compiler and runtime process limits

Loupe treats the compiler and generated native executables as external process
trees. Both paths use the same bounded runner instead of `capture_output` or an
unbounded `communicate` call.

The runner:

- launches a new process group on POSIX systems;
- streams stdout and stderr through capped temporary spool files;
- computes SHA-256 over every byte observed before termination;
- retains a bounded UTF-8 diagnostic excerpt;
- stops the complete process group after a wall-clock timeout or output overflow;
- sends `SIGTERM`, waits briefly, and escalates to `SIGKILL`;
- applies CPU, address-space, file-size, and process-count limits where POSIX
  resource limits are available.

## Override precedence

For each setting, an explicit CLI option wins over its matching environment
variable. The environment wins over the built-in default. Runtime sidecar
`timeout_seconds` supplies the default runtime timeout before environment and CLI
overrides are considered.

```sh
uv run loupe capture input.weave -o build/input.loupe \
  --compiler-timeout-seconds 90 \
  --compiler-output-bytes 4194304

uv run loupe audit input.weave \
  --compiler-timeout-seconds 90 \
  --compiler-output-bytes 4194304 \
  --runtime-timeout-seconds 3 \
  --runtime-output-bytes 262144
```

All numeric settings must be positive. Invalid CLI or environment values fail the
invocation rather than silently disabling a limit.

## Defaults

| Limit | Compiler | Runtime |
| --- | ---: | ---: |
| Wall-clock timeout | 120 seconds | sidecar, default 5 seconds |
| Output ceiling | 8 MiB per stream | 1 MiB per stream |
| Stored diagnostic excerpt | 64 KiB per stream | 16 KiB per stream |
| CPU time | at least 120 seconds | at least 6 seconds |
| Address space | 4 GiB | 512 MiB |
| File size | 1 GiB | 64 MiB |
| Additional task budget | 256 | 64 |

When a wall-clock override exceeds the default CPU limit, Loupe raises the CPU
limit to at least the rounded timeout plus one second. This prevents the CPU limit
from unexpectedly firing before the requested wall-clock deadline.

Linux `RLIMIT_NPROC` is UID-wide and counts tasks, including threads. An absolute
value therefore includes unrelated work already running for the same real user.
Loupe interprets the configured process count as additional task headroom. It
counts the current user's Linux tasks immediately before launch and adds the
configured budget. The process result records this effective kernel ceiling. On
platforms where a safe baseline cannot be observed, the configured value is
applied directly.

Compiler builds and explicitly unsafe direct runtime cases apply that ceiling in
the outer runner. Secure runtime cases cannot do so because a setuid Bubblewrap
launcher may need to fork an unprivileged helper while constructing the sandbox.
Loupe therefore supervises Bubblewrap externally without `RLIMIT_NPROC`, then runs
`prlimit --nproc=SOFT:HARD` inside the completed sandbox immediately before the
audited executable. Every other limit remains enforced by the outer supervisor.
Evidence distinguishes `runner-rlimit` from delegated `sandbox-prlimit` handling.

## Environment variables

Replace `KIND` with `COMPILER` or `RUNTIME`:

- `WEAVE_LOUPE_KIND_TIMEOUT_SECONDS`
- `WEAVE_LOUPE_KIND_OUTPUT_BYTES`
- `WEAVE_LOUPE_KIND_EXCERPT_BYTES`
- `WEAVE_LOUPE_KIND_CPU_SECONDS`
- `WEAVE_LOUPE_KIND_ADDRESS_SPACE_BYTES`
- `WEAVE_LOUPE_KIND_FILE_SIZE_BYTES`
- `WEAVE_LOUPE_KIND_PROCESS_COUNT`

For example:

```sh
export WEAVE_LOUPE_COMPILER_TIMEOUT_SECONDS=180
export WEAVE_LOUPE_COMPILER_OUTPUT_BYTES=$((16 * 1024 * 1024))
export WEAVE_LOUPE_RUNTIME_TIMEOUT_SECONDS=10
export WEAVE_LOUPE_RUNTIME_OUTPUT_BYTES=$((2 * 1024 * 1024))
```

The existing sandbox controls remain separate. Runtime cases require Bubblewrap
and util-linux `prlimit` unless the explicit local-only
`WEAVE_LOUPE_UNSAFE_NO_SANDBOX=1` override is set; that unsafe override remains
forbidden in GitHub Actions. Nonstandard executable locations can be supplied
with `WEAVE_LOUPE_BWRAP` and `WEAVE_LOUPE_PRLIMIT`.

## Termination evidence

Every bounded result uses `weave-loupe-process-result-v1` and records:

- `termination_reason`: `exited`, `signaled`, `timed_out`, or `output_limit`;
- normal exit code, raw return code, and terminating signal;
- elapsed wall-clock seconds;
- streams that exceeded the byte ceiling;
- the complete effective limit envelope;
- whether NPROC was applied by the runner or delegated to the sandbox;
- stdout and stderr observed bytes, stored bytes, truncated bytes, SHA-256,
  overflow state, and diagnostic text.

The stream digest covers all bytes Loupe observed before the process tree was
terminated. It cannot describe bytes an infinite or killed process would have
produced later.

Compiler evidence is stored under `compiler.execution` in `bundle.json`.
Successful and failed captures therefore retain the exact effective policy and
failure reason. For shell compatibility, compiler timeouts map to exit code `124`,
output overflow maps to `125`, and signal termination maps to `128 + signal`.
The structured execution object remains the authoritative distinction.

Runtime matrices record the effective sandbox policy and process limits at the
top level. Each case records its own termination reason, elapsed time, signal,
process-count enforcement location, stream hashes, byte counts, excerpts, and
overflow flags. A timeout, overflow, or signal is a deterministic runtime failure
even when sampled output happens to match an expectation.

## Platform behavior

Wall-clock limits, bounded output capture, and process supervision apply on every
supported platform. POSIX resource limits and process-group signaling are applied
where available. The evidence field `resource_limits_supported` states whether
those kernel resource limits were active for the invocation.
