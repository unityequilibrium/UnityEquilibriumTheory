import json
from decimal import Decimal
from datetime import datetime, timezone

import httpx
import pytest

from docs.knowledge_base.api_client import CostTracker, OpenRouterClient, BudgetExceeded, UnresolvedCost
from docs.knowledge_base.cost_dashboard import CostDashboard


@pytest.fixture
def tracker(tmp_path):
    return CostTracker(tmp_path / 'cost.jsonl')


def test_unknown_is_not_free(tracker):
    entry = tracker.log_call('a','unlisted',12,3)
    assert entry.cost_usd is None and entry.cost_status == 'unknown'
    assert CostDashboard(tracker.log_file).agent_summary()['a']['unknown_calls'] == 1


def test_restart_preserves_actual(tracker):
    tracker.log_call('a','m',12,3,provider_cost=.02,experiment_id='pilot')
    fresh = CostTracker(tracker.log_file)
    assert fresh.experiment_total('pilot') == Decimal('.02')
    assert fresh.get_daily_total('a') == .02


def test_experiment_survives_day_boundary(tracker):
    tracker.log_file.write_text(json.dumps({'timestamp':'2020-01-01T00:00:00+00:00',
        'agent_id':'a','experiment_id':'pilot','cost_usd':1.99})+'\n')
    with tracker.exclusive(), pytest.raises(BudgetExceeded):
        tracker.reserve('a','m',.02,'pilot',2)


def test_duplicate_runner_lock(tracker):
    other = CostTracker(tracker.log_file)
    with tracker.exclusive(), pytest.raises(UnresolvedCost):
        with other.exclusive():
            pass


def test_restart_keeps_reservation(tracker):
    with tracker.exclusive():
        tracker.reserve('a','m',.02,'pilot',2)
    fresh = CostTracker(tracker.log_file)
    with fresh.exclusive(), pytest.raises(UnresolvedCost):
        fresh.reserve('a','m',.02,'pilot',2)


def test_settlement_not_double_counted(tracker):
    with tracker.exclusive():
        request = tracker.reserve('a','m',.02,'pilot',2)
        tracker.log_call('a','m',5,2,request_id=request,experiment_id='pilot',
            provider_cost=.01,reservation=.02)
    assert tracker.experiment_total('pilot') == Decimal('.01')
    assert CostDashboard(tracker.log_file).agent_summary()['a']['calls'] == 1


def test_unknown_settlement_keeps_hold(tracker):
    with tracker.exclusive():
        request = tracker.reserve('a','m',.02,'pilot',2)
        tracker.log_call('a','m',5,2,request_id=request,experiment_id='pilot',reservation=.02)
    assert tracker.experiment_total('pilot') == Decimal('.02')
    assert tracker.effective_entries()[0]['state'] == 'unresolved'


def test_legacy_display_not_actual(tracker):
    tracker.log_file.write_text(json.dumps({'timestamp':datetime.now(timezone.utc).isoformat(),
        'agent_id':'a','cost_usd':.1,'model':'m'})+'\n')
    row = CostDashboard(tracker.log_file).agent_summary()['a']
    assert row['reported_usd'] == 0 and row['estimated_usd'] == .1 and row['legacy_calls'] == 1
    assert len(CostDashboard(tracker.log_file).load_entries(days=1)) == 1


def test_invalid_ledger_fails_closed(tracker):
    tracker.log_file.write_text('{broken\n')
    with tracker.exclusive(), pytest.raises(UnresolvedCost):
        tracker.reserve('a','m',.01,'pilot',2)


def test_environment_overrides_config(tracker, monkeypatch):
    monkeypatch.setenv('OPENROUTER_KEY_DEFAULT','env-test')
    with OpenRouterClient('https://openrouter.ai/api/v1',{'default':'file-test'},
        {'local_data':{'model':'m'}},tracker) as client:
        assert client._get_key('local_data') == 'env-test'


@pytest.fixture
def client(tracker):
    value = OpenRouterClient('https://openrouter.ai/api/v1',{'default':'test'},
        {'local_data':{'model':'m','daily_budget_usd':0}},tracker)
    value.experiment_id = 'pilot'
    value.experiment_limit = 2
    value.price_snapshot = {'m':{'pricing':{'prompt':Decimal('.000001'),
        'completion':Decimal('.000001'),'request':Decimal(0)},
        'fetched_at':datetime.now(timezone.utc).isoformat(),'remaining':Decimal(10)}}
    yield value
    value.close()


def test_timeout_blocks_later_calls(client):
    def timeout(request):
        raise httpx.ReadTimeout('test',request=request)
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(timeout))
    with pytest.raises(httpx.ReadTimeout):
        client.chat('local_data',[{'role':'user','content':'hello'}],max_tokens=10)
    with pytest.raises(UnresolvedCost):
        client.chat('local_data',[{'role':'user','content':'hello'}],max_tokens=10)


def test_over_budget_sends_nothing(client):
    called = []
    def handler(request):
        called.append(request)
        raise AssertionError('must not send')
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(handler))
    client.experiment_limit = .000001
    with pytest.raises(BudgetExceeded):
        client.chat('local_data',[{'role':'user','content':'hello'}],max_tokens=10)
    assert called == []


def test_chat_still_returns_string(client):
    def handler(request):
        body = json.loads(request.content)
        assert body['provider']['allow_fallbacks'] is False
        return httpx.Response(200,json={'usage':{'prompt_tokens':5,'completion_tokens':2,'cost':.001},
            'choices':[{'message':{'content':'ok'}}]})
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(handler))
    assert client.chat('local_data',[{'role':'user','content':'hello'}],max_tokens=10) == 'ok'


def test_nonfinite_cost_rejected(tracker):
    with pytest.raises(UnresolvedCost):
        tracker.log_call('a','m',1,1,provider_cost=float('nan'))


def test_unknown_without_reservation_stops_spending(tracker):
    tracker.log_call('a','unlisted',10,5)
    with tracker.exclusive(), pytest.raises(UnresolvedCost):
        tracker.reserve('a','m',.01,'pilot',2)


def test_missing_provider_cost_holds_budget(client):
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(lambda request:
        httpx.Response(200,json={'usage':{'prompt_tokens':4},'choices':[{'message':{'content':'text'}}]})))
    with pytest.raises(UnresolvedCost):
        client.chat('local_data',[{'role':'user','content':'hello'}],max_tokens=10)
    assert client.cost_tracker.experiment_total('pilot') > 0


def test_embeddings_return_vectors(client):
    client._client.close()
    client._client = httpx.Client(transport=httpx.MockTransport(lambda request:
        httpx.Response(200,json={'usage':{'prompt_tokens':4,'cost':.001},'data':[{'embedding':[1.0,2.0]}]})))
    assert client.embed(['test'],agent_id='local_data') == [[1.0,2.0]]


def test_missing_configuration_does_not_call_api(tmp_path, monkeypatch):
    from docs.knowledge_base import foundation_pilot
    monkeypatch.setattr(foundation_pilot, 'RUN', tmp_path)
    result = foundation_pilot.run_live([],tmp_path/'absent.toml')
    assert result['status'] == 'blocked' and result['calls'] == 0
    assert not (tmp_path/'api-costs.jsonl').exists()
