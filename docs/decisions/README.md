# Architecture Decision Records (ADRs)

This directory contains architecture decision records for FractalTrader, documenting key technical decisions made during development.

## Format

Each ADR follows this structure:
- **Title**: NNNN-descriptive-title.md (sequential numbering)
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Date**: YYYY-MM-DD
- **Context**: What problem are we solving?
- **Decision**: What did we decide?
- **Consequences**: What are the trade-offs?

## Index

| ADR | Title | Date | Status | Sprint |
|-----|-------|------|--------|--------|
| [0001](0001-circuit-breaker-false-triggers.md) | Circuit Breaker False Triggers Fix | 2026-01-05 | Accepted | 4 |
| [0004](0004-testnet-simulation-mode.md) | Testnet Simulation Mode Design | 2026-01-04 | Accepted | 4 |

## Gap Numbers

ADR numbers 0002 and 0003 are reserved for future documentation of decisions made during Sprint 4:
- **0002**: State Persistence JSON Serialization Fix
- **0003**: BTC Tick Size Rounding

These decisions were implemented but not formally documented as ADRs. We may backfill these entries for completeness.

---

## Creating New ADRs

When making a significant architectural decision:

1. **Create a new file**: Use next sequential number (0005, 0006, etc.)
2. **Use the template**: Follow existing ADR format
3. **Update this index**: Add entry to the table above
4. **Link from related docs**: Reference ADR in code comments, PRs, or sprint reports

### Template

```markdown
# ADR NNNN: [Short Title]

**Status**: Proposed | Accepted | Deprecated | Superseded
**Date**: YYYY-MM-DD
**Deciders**: [Names or roles]

## Context

[Describe the problem or situation requiring a decision]

## Decision

[Describe what we decided to do]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Trade-off 1]
- [Trade-off 2]

### Risks
- [Risk 1]
- [Mitigation]

## Implementation

[Brief overview of how this was implemented]

## Alternatives Considered

### Option 1: [Alternative approach]
- Pros: [...]
- Cons: [...]
- Why rejected: [...]

### Option 2: [Another alternative]
- Pros: [...]
- Cons: [...]
- Why rejected: [...]

## References

- [Related PR]
- [Related Issue]
- [External documentation]
```

---

## Resources

- [Architecture Decision Records (ADR) Guide](https://adr.github.io/)
- [When to Write an ADR](https://github.com/joelparkerhenderson/architecture-decision-record#when-should-we-write-an-adr)
- [ADR Best Practices](https://www.thoughtworks.com/en-us/insights/blog/architecture/architecture-decision-records)

---

**Last Updated**: 2026-01-07
**Total ADRs**: 2 (documented), 2 (pending backfill)
