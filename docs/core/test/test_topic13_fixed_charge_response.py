import pytest
from docs.scripts.audit.audit_topic13_fixed_charge_response import constrained_derivative


def test_implicit_constraint_chain_rule():
    # e=T*T+mu*mu, n=T+2*mu, at T=3,mu=2.
    assert constrained_derivative(6,4,1,2)==4
    assert constrained_derivative(6,4,0,2)==6


def test_unstable_or_singular_susceptibility_rejected():
    for n_mu in (0,-1,float('nan')):
        with pytest.raises(ValueError):constrained_derivative(1,1,1,n_mu)
