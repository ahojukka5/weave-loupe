# LLM endpoint transport and identity

Loupe treats the URL used for the network connection and the endpoint identity
published in evidence as two different values.

The **transport URL** is the configured `WEAVE_LLM_ENDPOINT`. Loupe passes this
private value to the OpenAI-compatible client without rewriting HTTP to HTTPS.
It may contain connection-only details required by a local or proxied endpoint.
The transport URL is never included in reports, request metadata, configuration
representations, or Loupe error messages.

The **public endpoint identity** is derived deterministically from the transport
URL. Loupe records this value in reports, uses it in request hashes, and compares
it during `verify-report`.

## Secure defaults

HTTPS endpoints are accepted normally:

```sh
export WEAVE_LLM_ENDPOINT=https://integrate.api.nvidia.com/v1
```

Plain HTTP is accepted by default only for loopback hosts:

```sh
export WEAVE_LLM_ENDPOINT=http://localhost:8000/v1
export WEAVE_LLM_API_KEY=local
uv run loupe audit docs/audit/fibonacci.weave \
  --model local-model \
  --report-out build/fibonacci-local.md
```

The loopback policy includes:

- `localhost`, case-insensitively and with an optional trailing DNS dot;
- every IPv4 address in `127.0.0.0/8`; and
- IPv6 `::1`.

A non-loopback HTTP endpoint is rejected unless the caller explicitly accepts
the insecure transport:

```sh
uv run loupe audit docs/audit/fibonacci.weave \
  --allow-unsafe-http \
  --model internal-model
```

Both `audit` and `verify-report` also accept the shared environment override:

```sh
export WEAVE_LLM_ALLOW_UNSAFE_HTTP=1
```

Accepted true values are `1`, `true`, `yes`, and `on`; accepted false values are
`0`, `false`, `no`, and `off`. Any other value is an error.

`verify-report --allow-unsafe-http` provides the same explicit override for one
offline verification. Verification never contacts the endpoint; the option or
environment value confirms that the insecure transport identity is intentional.

## Public identity normalization

The public identity:

- preserves the configured `http` or `https` scheme;
- lower-cases and IDNA-normalizes host names;
- compresses IPv6 addresses and restores bracket notation;
- removes port `80` from HTTP and port `443` from HTTPS;
- retains non-default ports;
- removes trailing path slashes; and
- removes URL user information, query strings, and fragments.

Examples:

| Transport URL | Public identity |
| --- | --- |
| `http://LOCALHOST:80/v1/` | `http://localhost/v1` |
| `http://127.42.0.8:8000/v1/` | `http://127.42.0.8:8000/v1` |
| `http://[0:0:0:0:0:0:0:1]:80/v1/` | `http://[::1]/v1` |
| `https://Example.TEST:443/v1/` | `https://example.test/v1` |
| `https://user:secret@example.test/v1?token=x#part` | `https://example.test/v1` |

Because request provenance uses the public identity, changing only URL
credentials, query parameters, or fragments does not expose them or change the
published request hash. Changing the scheme, host, non-default port, or path does
change the identity and invalidates older reports.

## Error redaction

Loupe does not interpolate the private transport URL, API key, provider exception
message, or response representation into its own errors. Failures identify the
sanitized endpoint identity or HTTP status only. This keeps connection credentials
and secret-bearing URL components out of normal terminal output and generated
workflow diagnostics.

The underlying HTTP client can still have independent debug logging. Do not enable
third-party wire logging when the configured transport URL contains secrets.
