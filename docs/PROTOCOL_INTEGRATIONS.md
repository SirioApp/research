# Protocol Integrations

This document tracks protocol-level integrations for Backed Research Agent.

## Current state

No protocol-bound execution path is enabled in the current stable release.
The current pipeline is provider-driven (web/docs + data APIs + optional LLM refinement).

## Planned integration: x402 on MegaETH

Status: **planned / in design**

### Goal
Integrate x402 payment/authentication flow on MegaETH to support:
- metered premium research runs
- authenticated access tiers for advanced diligence modules
- machine-to-machine settlement for report execution

### Proposed integration surface

1. Request gating
- Add middleware-like authorization layer before expensive analysis paths.
- Validate x402 payment proof / session entitlement.

2. Policy routing
- Map entitlement tiers to feature flags:
  - baseline underwriting
  - deep diligence mode
  - extended provider calls
  - historical benchmarking depth

3. Auditability
- Persist run-level entitlement metadata with deterministic run IDs.
- Include non-sensitive payment/auth references in run logs.

4. Failure semantics
- If x402 validation fails, return explicit authorization error.
- Preserve deterministic non-premium mode for public/basic usage.

### Technical notes

- Integration will be additive, not a rewrite.
- Core scoring/risk modules remain protocol-agnostic.
- x402/MegaETH adapter will be isolated behind a dedicated integration boundary.

### Security notes

- No private keys or sensitive auth payloads in analytics output.
- Strict secret management for signer/session material.
- Threat model includes replay protection and request tampering controls.

## Non-goals (initial phase)

- On-chain strategy execution.
- Automated capital deployment.
- Custody/account management inside the agent runtime.
