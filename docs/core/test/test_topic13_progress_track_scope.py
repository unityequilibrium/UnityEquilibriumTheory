from docs.scripts.audit.render_topic13_closure_progress import track_summary, build_payload, render_markdown


def test_track_statuses_do_not_leak_between_materials():
    t=track_summary({'closure_tracks':{'o2_he4_core_ready':{'status':'CLOSED_FOR_CORE'},'graphite_ttg_external_validation':{'status':'OPEN'}}})
    assert t['o2_he4_core_ready']['status']=='CLOSED_FOR_CORE'
    assert t['graphite_ttg_external_validation']['status']=='OPEN'
    assert track_summary({})['o2_he4_core_ready']['status']=='NOT_REPORTED'


def test_current_report_preserves_scopes_and_exposure():
    p=build_payload();md=render_markdown(p)
    assert p['canonical_status']['full_core_unlock'] is True
    assert p['closure_tracks']['o2_he4_core_ready']['status']=='CLOSED_FOR_CORE'
    assert p['closure_tracks']['graphite_ttg_external_validation']['status']=='OPEN'
    assert p['holdout_context_review']['incidental_public_summary_exposure'] is True
    assert 'REVIEW_REQUIRED' in md
    assert 'No input package is accepted for Full Topic 13 Core closure.' not in md
