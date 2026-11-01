import httpx
import pytest
from docs.knowledge_base.jev_pilot import cases, select, MODEL
from docs.knowledge_base.api_client import OpenRouterClient, CostTracker

def answers():
    return {d['id']:{'type':'choice','choice':'drop','confidence':.99,
        'probabilities':{'drop':.99,'keep':.005,'unknown':.005}} for d in cases()[0]['documents']}

def test_mandatory_is_kept_even_on_drop():
    kept,_ = select(cases()[0],answers())
    assert [d['id'] for d in kept] == ['method']

def test_low_confidence_is_kept():
    value = answers()
    value['contrary']['confidence'] = .2
    assert 'contrary' in {d['id'] for d in select(cases()[0],value)[0]}

@pytest.mark.parametrize('mutation',['missing','nan','bad-choice'])
def test_bad_decisions_rejected(mutation):
    value = answers()
    if mutation=='missing': value.pop('method')
    if mutation=='nan': value['method']['confidence']=float('nan')
    if mutation=='bad-choice': value['method']['choice']='proved'
    with pytest.raises(ValueError): select(cases()[0],value)

def test_decisions_endpoint_and_usage(tmp_path):
    from decimal import Decimal
    from datetime import datetime, timezone
    tracker = CostTracker(tmp_path/'cost.jsonl')
    client = OpenRouterClient('https://openrouter.ai/api/v1',{'default':'test'},
        {'local_data':{'model':MODEL}},tracker)
    client.experiment_id='pilot'; client.experiment_limit=2
    client.price_snapshot={MODEL:{'pricing':{'prompt':Decimal('.000000042'),
        'completion':Decimal(0),'request':Decimal(0)},'remaining':Decimal(2),
        'fetched_at':datetime.now(timezone.utc).isoformat()}}
    def handler(request):
        assert str(request.url)=='https://openrouter.ai/api/alpha/decisions'
        return httpx.Response(200,json={'answers':{},'usage':{'input_tokens':100,'output_tokens':20,'cost':.0000042}})
    client._client.close()
    client._client=httpx.Client(transport=httpx.MockTransport(handler))
    with client:
        client.decide('local_data',{}, {})
    entry=tracker.effective_entries()[0]
    assert entry['input_tokens']==100 and entry['output_tokens']==20

def test_decision_preflight_uses_modality_listing(tmp_path):
    tracker=CostTracker(tmp_path/'cost.jsonl')
    client=OpenRouterClient('https://openrouter.ai/api/v1',{'default':'test'},
        {'local_data':{'model':MODEL}},tracker)
    def handler(request):
        if request.url.path.endswith('/models'):
            assert request.url.params['output_modalities']=='decisions'
            return httpx.Response(200,json={'data':[{'id':MODEL,'pricing':{'prompt':'0.000000042','completion':'0'}}]})
        if request.url.path.endswith('/key'):
            return httpx.Response(200,json={'data':{'limit_remaining':2}})
        return httpx.Response(200,json={'data':{'total_credits':2,'total_usage':0}})
    client._client.close()
    client._client=httpx.Client(transport=httpx.MockTransport(handler))
    with client:
        assert client.preflight('local_data')['model']==MODEL
