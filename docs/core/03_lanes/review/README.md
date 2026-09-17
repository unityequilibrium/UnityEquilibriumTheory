# Review and observable support lane

This lane contains support and measurement adapters that connect a physical
state result to a declared diagnostic record. They are not equation sources
and their organization status must not be read as physics verification.

The matter-space observable adapter remains normalized-only and retains its
explicit `mass_density_mapping` and SI `BLOCKED` boundaries until a dimensional
measurement operator is independently defined.

- `uet_observables.py` — legacy observable helpers retained for topic compatibility;
  their cosmology/galaxy interpretations remain review-only until units,
  measurement operators, uncertainty, and external evidence are complete.