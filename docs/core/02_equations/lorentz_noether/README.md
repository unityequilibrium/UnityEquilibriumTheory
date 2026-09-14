# Lorentz and Noether equation family

This directory is the canonical organization area for the legacy Lorentz
diagnostics and the Noether/phase-field mapping support.

The current migration starts with `uet_lorentz.py`.  Its Lorentz matrices and
diagnostics are compatibility utilities, not a proof that every UET operator
is Lorentz invariant.  The Noether sources are migrated separately after
their shared legacy dependencies and mapping tests are checked.

The root imports under `docs.core.uet_lorentz` remain compatibility shims.
Organization status is independent of physics evidence status; the current
family contract still limits claims to support utilities and mapping layers.
