# Indicator admission policy

User decision: 15 November 2026.

From now on, add only completely new, meaningful indicator concepts to Datacritus.

- A new source, frequency, unit, language, geographic breakdown, or updated observation is not a new indicator.
- Treat alternative sources, methodological variants, and granular breakdowns of existing concepts as enrichment of the existing indicator, not an increase in the headline count.
- Check definitions, populations, denominators, instruments, scope and overlap across the entire current catalogue before admitting anything.
- Document the distinct question answered and why no existing indicator already answers it.
- Require explicit reuse terms, verified observations, clear metadata, reproducible retrieval and validation.
- Weekly refresh must preserve the last validated snapshot on failure, retain revisions/provisional flags, and update successful-refresh metadata only after validation.

The data.gov.gr audit proposed 21 distinct series under its earlier scope. None has been imported. The 21 is a candidate admission count, not blanket authorization or proof of compliance with this stricter concept-only rule. Recheck each candidate under this policy before importing; reduce the count where a candidate is only a breakdown or alternative representation of an existing concept.

The 12 audited Bank of Greece source resources are publicly retrievable and suitable for a scheduled weekly check in principle. The connector, latest-resource resolution, freshness/revision monitoring and validation still need implementation. Two successful downloads do not establish long-term availability. Weekly checks do not imply weekly publication of new observations.
