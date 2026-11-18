# Archived Topic 0.10 tests

Archived 2026-11-18 in core alignment W8, applying the owner's decision (chat) to archive failing legacy tests rather than repair them.
These test the O(2) helium fluid lane, labelled C in `core/CORE_ALIGNMENT_REGISTER.tsv`. None is a physics test and none is pinned by a calculation contract.
They fail because stored prior-source hashes and archive identities predate the 2026-11-14 root move. The 18 files hold 67 tests, of which 33 failed or errored.
The `archived_` prefix keeps pytest and the CI changed-test step from collecting them. Content is unchanged (git records each as a rename).
Provenance: LEGACY_UNREVIEWED. Do not use these files as evidence.

| Archived file | Original path |
|---|---|
| `03_Research/archived_test_fluid_core_o2_common_flow.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_common_flow.py` |
| `03_Research/archived_test_fluid_core_o2_continuum_form.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_continuum_form.py` |
| `03_Research/archived_test_fluid_core_o2_current_bound.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_current_bound.py` |
| `03_Research/archived_test_fluid_core_o2_current_ward.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_current_ward.py` |
| `03_Research/archived_test_fluid_core_o2_density_backreaction.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_density_backreaction.py` |
| `03_Research/archived_test_fluid_core_o2_flow_hessian.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_flow_hessian.py` |
| `03_Research/archived_test_fluid_core_o2_goldstone_collision.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_goldstone_collision.py` |
| `03_Research/archived_test_fluid_core_o2_goldstone_galerkin.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_goldstone_galerkin.py` |
| `03_Research/archived_test_fluid_core_o2_ideal_modes.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_ideal_modes.py` |
| `03_Research/archived_test_fluid_core_o2_infrared_trials.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_infrared_trials.py` |
| `03_Research/archived_test_fluid_core_o2_interacting_method.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_interacting_method.py` |
| `03_Research/archived_test_fluid_core_o2_vector_refinement.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_core_o2_vector_refinement.py` |
| `03_Research/archived_test_fluid_second_sound_mode_eligibility.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_second_sound_mode_eligibility.py` |
| `03_Research/archived_test_fluid_two_fluid_eos_reference.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_two_fluid_eos_reference.py` |
| `03_Research/archived_test_fluid_vector_state_contract.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_vector_state_contract.py` |
| `03_Research/archived_test_fluid_vector_variational_origin.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_fluid_vector_variational_origin.py` |
| `03_Research/archived_test_he4_entropy_source_reference.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_he4_entropy_source_reference.py` |
| `03_Research/archived_test_he4_fixed_constraint_eos_source.py` | `topics/0.10_Fluid_Dynamics_Chaos/Code/03_Research/test_he4_fixed_constraint_eos_source.py` |
