import numpy as np
from docs.scripts.audit.audit_topic13_local_quadratic_bounds import segment_constants,quadratic_certificate


def test_segment_envelopes_cover_gradients_including_origin_crossing():
    target=np.array([2.,1.,-.4]); p=np.array([[-2.,-1.,.4],[3.,2.,1.],[2.,1.,-.4]])
    bound=segment_constants(p,target,1.)
    for i,endpoint in enumerate(p):
        for t in np.linspace(0,1,101):
            q=target+t*(endpoint-target); d=1+q@q
            grad1=np.array([q[1],q[0],0])/d-2*q[0]*q[1]*q/d**2
            grad2=-q/d**1.5
            assert np.linalg.norm(grad1)<=bound[i,0]+1e-14
            assert np.linalg.norm(grad2)<=bound[i,1]+1e-14


def test_far_segments_tighten_global_bound():
    b=segment_constants(np.array([[11.,0.,0.]]),np.array([10.,0.,0.]),1.)
    assert b[0,0]<.2 and b[0,1]<.01


def test_quadratic_certificate_covers_all_coefficient_directions():
    a=np.array([[1.,2.],[-.5,1.],[3.,-.2]])
    error=np.array([[.1,-.03],[.02,.04],[-.05,.08]])
    cert=quadratic_certificate(a,a+error,np.abs(error),[1.,2.,3.])
    assert cert["error_norm"]<=cert["error_bound"]
    delta=np.asarray(cert["mapped_gram"])-cert["exact_gram"]
    for angle in np.linspace(0,2*np.pi,41):
        c=np.array([np.cos(angle),np.sin(angle)])
        assert abs(c@delta@c)<=cert["error_bound"]+1e-14
