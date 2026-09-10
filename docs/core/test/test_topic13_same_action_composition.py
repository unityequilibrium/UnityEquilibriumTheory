from dataclasses import replace
import pytest
from docs.scripts.audit.audit_topic13_same_action_composition import (
    config_identity, require_same_config, natural_bridge_config,
    FiniteTemperatureO2QuasiparticleConfig,
)


def test_equal_coordinates_cannot_override_different_action():
    config = natural_bridge_config()
    with pytest.raises(ValueError):
        require_same_config([config, FiniteTemperatureO2QuasiparticleConfig()])
    changed = replace(config, eos=replace(config.eos, matter=replace(config.eos.matter, response_coupling=0.)))
    with pytest.raises(ValueError):
        require_same_config([config, changed])


def test_full_config_identity_includes_numerical_controls():
    config = natural_bridge_config()
    require_same_config([config, replace(config)])
    assert config_identity(config) != config_identity(replace(config, quadrature_order=192))
    with pytest.raises(ValueError):
        require_same_config([])
