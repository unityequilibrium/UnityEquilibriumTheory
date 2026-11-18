# Archived legacy core tests

Archived 2026-11-18 in core alignment W8 by owner decision (chat): the failing legacy tests are archived rather than repaired.
Every file here tests a lane labelled C in `core/CORE_ALIGNMENT_REGISTER.tsv`. None is a physics test and none is pinned by a calculation contract.
The `archived_` prefix keeps pytest and the CI changed-test step from collecting them. Content is unchanged (git records each as a rename).
Provenance: LEGACY_UNREVIEWED. Do not use these files as evidence.

| Archived file | Original path | Why it fails |
|---|---|---|
| `05_tests/equation/root/archived_test_gr_noether_phase_field_map_alignment.py` | `core/05_tests/equation/root/test_gr_noether_phase_field_map_alignment.py` | needs a regenerated Noether gate, but the BaTiO3 publication pins that gate to its published version |
| `05_tests/equation/root/archived_test_topic13_continuum_action_umklapp_no_go.py` | `core/05_tests/equation/root/test_topic13_continuum_action_umklapp_no_go.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/regression/root/archived_test_topic13_anisotropic_thermoelastic_response_bridge.py` | `core/05_tests/regression/root/test_topic13_anisotropic_thermoelastic_response_bridge.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/regression/root/archived_test_topic13_calorine_lattice_interface_inputs.py` | `core/05_tests/regression/root/test_topic13_calorine_lattice_interface_inputs.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/regression/root/archived_test_topic13_lattice_momentum_relaxing_heat_parent.py` | `core/05_tests/regression/root/test_topic13_lattice_momentum_relaxing_heat_parent.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/regression/root/archived_test_topic13_material_interface_factor_resolution.py` | `core/05_tests/regression/root/test_topic13_material_interface_factor_resolution.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/regression/root/archived_test_topic13_material_lattice_interface_contract.py` | `core/05_tests/regression/root/test_topic13_material_lattice_interface_contract.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/regression/root/archived_test_topic13_mp48_mode_resolved_csrc_diagnostic.py` | `core/05_tests/regression/root/test_topic13_mp48_mode_resolved_csrc_diagnostic.py` | needs a private raw data file that is not committed |
| `05_tests/regression/root/archived_test_topic13_nist_srm_3600_heat_capacity_boundary.py` | `core/05_tests/regression/root/test_topic13_nist_srm_3600_heat_capacity_boundary.py` | needs a private raw data file that is not committed |
| `05_tests/regression/root/archived_test_topic13_oxford_tgs_comparator_provenance.py` | `core/05_tests/regression/root/test_topic13_oxford_tgs_comparator_provenance.py` | needs a private raw data file that is not committed |
| `05_tests/regression/root/archived_test_topic13_scalar_thermoelastic_response_bridge.py` | `core/05_tests/regression/root/test_topic13_scalar_thermoelastic_response_bridge.py` | its generator still imports docs.core or expects docs/core path text and stored hashes from before the 2026-11-14 root move |
| `05_tests/equation/root/archived_test_uet_noether_mapping_links.py` | `core/05_tests/equation/root/test_uet_noether_mapping_links.py` | checks that the Noether verifier test exists; that test is archived above |
