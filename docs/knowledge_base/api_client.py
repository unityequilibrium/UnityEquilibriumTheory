"""OpenRouter client with persistent, fail-closed cost accounting.

chat() still returns str; embed() still returns vectors. No prompts or keys are logged.
Reservations survive restarts; uncertain charges must be reconciled before another call.
"""
from __future__ import annotations
import json
import os
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Optional
import tomllib
try:
    import httpx
except ImportError:
    httpx = None

# Historical estimates only. Live requests require a fresh price snapshot.
_MODEL_PRICING = {
    # Embedding models
    "qwen/qwen3-embedding-8b": {"input": 0.01, "output": 0.0},
    "baai/bge-m3": {"input": 0.01, "output": 0.0},
    "google/gemini-embedding-001": {"input": 0.15, "output": 0.0},
    "openai/text-embedding-3-small": {"input": 0.02, "output": 0.0},
    "openai/text-embedding-3-large": {"input": 0.13, "output": 0.0},
    # Chat models
    "qwen/qwen3-coder-next": {"input": 0.07, "output": 0.30},
    "zhipu/glm-4.7-flash": {"input": 0.06, "output": 0.40},
    "deepseek/deepseek-v3.2": {"input": 0.25, "output": 0.38},
    "qwen/qwen3-30b-a3b:free": {"input": 0.0, "output": 0.0},
    "mistral/devstral-2": {"input": 0.05, "output": 0.22},
    # Marketing Agent
    "google/gemini-2.0-flash-001": {"input": 0.10, "output": 0.40},
}

class BudgetExceeded(RuntimeError):
    pass

class UnresolvedCost(RuntimeError):
    pass

@dataclass
class CostEntry:
    timestamp: str
    agent_id: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: Optional[float]
    cumulative_daily_usd: float
    endpoint: str
    success: bool = True
    error: Optional[str] = None
    request_id: str = ''
    experiment_id: str = 'default'
    cost_status: str = 'unknown'
    estimated_cost_usd: Optional[float] = None
    reserved_usd: float = 0.0
    state: str = 'settled'
    usage: Optional[dict] = None
    schema_version: int = 2

class CostTracker:
    def __init__(self, log_file: Path, alert_threshold: float = 1.0):
        self.log_file = Path(log_file)
        self.alert_threshold = alert_threshold
        self._locked = False

    def entries(self):
        if not self.log_file.exists():
            return []
        entries = []
        for line in self.log_file.read_text(encoding='utf-8').splitlines():
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict):
                    raise ValueError('Ledger entry is not an object')
                entries.append(row)
            except (ValueError,TypeError) as exc:
                raise UnresolvedCost('Malformed cost ledger; reconcile before spending') from exc
        return entries

    def effective_entries(self):
        merged = {}
        for index, entry in enumerate(self.entries()):
            key = entry.get('request_id') or f'legacy-{index}'
            merged[key] = entry
        return list(merged.values())

    @contextmanager
    def exclusive(self):
        if self._locked:
            yield
            return
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        lock = self.log_file.with_suffix(self.log_file.suffix + '.lock')
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise UnresolvedCost('Ledger already locked; inspect pending calls before recovery') from exc
        try:
            os.write(fd, str(os.getpid()).encode())
            self._locked = True
            yield
        finally:
            self._locked = False
            os.close(fd)
            lock.unlink()

    def _append(self, entry):
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.log_file.open('a',encoding='utf-8') as stream:
            stream.write(json.dumps(entry,ensure_ascii=False,allow_nan=False)+'\n')
            stream.flush()
            os.fsync(stream.fileno())

    @staticmethod
    def _amount(entry):
        amount = entry.get('cost_usd')
        if amount is None:
            amount = entry.get('reserved_usd', 0)
        value = Decimal(str(amount))
        if not value.is_finite() or value < 0:
            raise UnresolvedCost('Invalid amount in ledger')
        return value

    def get_daily_total(self, agent_id):
        today = datetime.now(timezone.utc).date().isoformat()
        return float(sum((self._amount(e) for e in self.effective_entries()
            if e.get('agent_id') == agent_id and e.get('timestamp','')[:10] == today),Decimal(0)))

    def get_total_daily_cost(self):
        today = datetime.now(timezone.utc).date().isoformat()
        return float(sum((self._amount(e) for e in self.effective_entries()
            if e.get('timestamp','')[:10] == today),Decimal(0)))

    def experiment_total(self, experiment_id):
        return sum((self._amount(e) for e in self.effective_entries()
            if e.get('experiment_id','default') == experiment_id),Decimal(0))

    def check_budget(self, agent_id, budget_limit):
        if budget_limit > 0 and self.get_daily_total(agent_id) >= budget_limit:
            raise BudgetExceeded('Daily budget exhausted')
        return True

    def reserve(self, agent_id, model, amount, experiment_id, experiment_limit, daily_limit=0):
        if not self._locked:
            raise RuntimeError('Reservation requires exclusive ledger lock')
        amount = Decimal(str(amount))
        if not amount.is_finite() or amount <= 0:
            raise UnresolvedCost('A positive conservative reservation is required')
        entries = self.effective_entries()
        if any(e.get('state') in {'reserved','unresolved'} or
               (e.get('cost_usd') is None and not e.get('request_id')) for e in entries):
            raise UnresolvedCost('Pending cost must be reconciled before paid calls')
        if experiment_limit <= 0 or self.experiment_total(experiment_id) + amount > Decimal(str(experiment_limit)):
            raise BudgetExceeded('Experiment cap would be exceeded')
        if daily_limit > 0 and Decimal(str(self.get_daily_total(agent_id))) + amount > Decimal(str(daily_limit)):
            raise BudgetExceeded('Daily cap would be exceeded')
        request_id = str(uuid.uuid4())
        self._append({'schema_version':2,'timestamp':datetime.now(timezone.utc).isoformat(),
            'request_id':request_id,'experiment_id':experiment_id,'agent_id':agent_id,
            'model':model,'reserved_usd':float(amount),'cost_usd':None,
            'state':'reserved','cost_status':'unknown'})
        return request_id

    def log_call(self, agent_id, model, input_tokens, output_tokens, endpoint='chat',
                 success=True, error=None, *, request_id=None, experiment_id='default',
                 provider_cost=None, usage=None, reservation=0):
        with self.exclusive():
            pricing = _MODEL_PRICING.get(model)
            estimate = ((input_tokens*pricing['input'] + output_tokens*pricing['output'])/1_000_000) if pricing else None
            cost = None
            if provider_cost is not None:
                parsed = Decimal(str(provider_cost))
                if not parsed.is_finite() or parsed < 0:
                    raise UnresolvedCost('Invalid provider-reported cost')
                cost = float(parsed)
            status = 'provider_reported' if cost is not None else ('estimated' if estimate is not None else 'unknown')
            # Estimates are informational; they never settle an actual reservation.
            state = 'settled' if cost is not None else 'unresolved'
            entry = CostEntry(datetime.now(timezone.utc).isoformat(),agent_id,model,
                input_tokens,output_tokens,cost,0.0,endpoint,success,error,
                request_id or str(uuid.uuid4()),experiment_id,status,estimate,reservation,state,
                {k:v for k,v in (usage or {}).items() if k in {'prompt_tokens','completion_tokens',
                    'input_tokens','output_tokens','total_tokens','cost','prompt_tokens_details','completion_tokens_details'}})
            other = sum((self._amount(e) for e in self.effective_entries()
                if e.get('request_id') != entry.request_id and e.get('agent_id') == agent_id
                and e.get('timestamp','')[:10] == entry.timestamp[:10]), Decimal(0))
            entry.cumulative_daily_usd = float(other + Decimal(str(cost if cost is not None else reservation)))
            self._append(asdict(entry))
            return entry

    def print_summary(self):
        print(json.dumps({'daily_accounted_usd':self.get_total_daily_cost(),
            'unresolved':sum(e.get('state') in {'reserved','unresolved'} for e in self.effective_entries())}))

class OpenRouterClient:
    def __init__(self, base_url, keys, agents, cost_tracker):
        if httpx is None:
            raise ImportError('httpx is required')
        self.base_url = base_url.rstrip('/')
        self.keys, self.agents, self.cost_tracker = keys, agents, cost_tracker
        self._client = httpx.Client(timeout=120.0)
        self.price_snapshot = {}
        self.experiment_id = 'default'
        self.experiment_limit = 0.0  # Explicit opt-in; no uncontrolled paid calls.

    @classmethod
    def from_config(cls, config_path):
        path = Path(config_path)
        config = tomllib.loads(path.read_text(encoding='utf-8-sig'))
        cost = config['cost_tracking']
        tracker = CostTracker(path.parent / cost['log_file'],cost.get('alert_threshold_usd',1))
        return cls(config['openrouter']['base_url'],config['openrouter'].get('keys',{}),config['agents'],tracker)

    def _get_key(self, agent_id):
        name = self.agents.get(agent_id,{}).get('key_name','default')
        key = (os.environ.get('OPENROUTER_KEY_'+name.upper()) or
               os.environ.get('OPENROUTER_KEY_DEFAULT') or self.keys.get(name) or self.keys.get('default'))
        if not key or key == 'sk-or-v1-CHANGEME':
            raise ValueError('OpenRouter key is not configured')
        return key

    def _get_model(self, agent_id):
        return self.agents[agent_id]['model']

    def preflight(self, agent_id):
        if self.base_url != 'https://openrouter.ai/api/v1':
            raise ValueError('Pilot requires the official OpenRouter endpoint')
        key = self._get_key(agent_id)
        model = self._get_model(agent_id)
        decision_model = model == 'typesafe/jev-1.13'
        models = self._client.get(self.base_url+'/models',
            params={'output_modalities':'decisions'} if decision_model else None)
        models.raise_for_status()
        record = next((r for r in models.json()['data'] if r['id']==model),None)
        if record is None:
            raise ValueError('Configured model is unavailable; no substitute selected')
        pricing = dict(record.get('pricing',{}))
        if decision_model:
            # Decisions model metadata declares only input/output token pricing.
            pricing.setdefault('request','0')
        required = ('prompt','completion','request')
        if any(k not in pricing for k in required):
            raise UnresolvedCost('Incomplete current price metadata')
        parsed = {k:Decimal(str(pricing[k])) for k in required}
        if any(not v.is_finite() or v < 0 for v in parsed.values()):
            raise UnresolvedCost('Invalid price metadata')
        if any(Decimal(str(v or 0)) != 0 for k,v in pricing.items() if k not in required):
            raise UnresolvedCost('Additional pricing components require explicit review')
        credit = self._client.get(self.base_url+'/key',headers={'Authorization':'Bearer '+key})
        credit.raise_for_status()
        data = credit.json()['data']
        remaining = data.get('limit_remaining')
        if remaining is not None and Decimal(str(remaining)) <= 0:
            raise BudgetExceeded('Provider key limit exhausted')
        balance = self._client.get(self.base_url+'/credits',headers={'Authorization':'Bearer '+key})
        balance.raise_for_status()
        credit_data = balance.json()['data']
        available = Decimal(str(credit_data['total_credits'])) - Decimal(str(credit_data['total_usage']))
        if available <= 0:
            raise BudgetExceeded('Account balance exhausted')
        self.price_snapshot[model] = {'pricing':parsed,'fetched_at':datetime.now(timezone.utc).isoformat(),
                                      'record':record,'remaining':min(available,Decimal(str(remaining))) if remaining is not None else available}
        return {'model':model,'pricing':{k:str(v) for k,v in parsed.items()},'available_usd':str(available)}

    def reservation_for(self, agent_id, payload):
        model = self._get_model(agent_id)
        snapshot = self.price_snapshot.get(model)
        if not snapshot:
            raise UnresolvedCost('Run preflight before calling a model')
        age = datetime.now(timezone.utc) - datetime.fromisoformat(snapshot['fetched_at'])
        if age.total_seconds() > 900:
            raise UnresolvedCost('Price snapshot expired; repeat preflight')
        # UTF-8 byte count deliberately overestimates text tokens; include template overhead.
        bound = len(json.dumps(payload,ensure_ascii=False).encode('utf-8')) + 4096
        prices = snapshot['pricing']
        amount = (Decimal(bound)*prices['prompt'] + Decimal(payload.get('max_tokens',0))*prices['completion'] + prices['request'])*Decimal('1.25')
        amount = max(amount, Decimal('0.000001'))
        if amount > snapshot['remaining']:
            raise BudgetExceeded('Provider credit cannot cover the reservation')
        return amount

    def _request(self, agent_id, payload, endpoint):
        key = self._get_key(agent_id)
        amount = self.reservation_for(agent_id,payload)
        model = self._get_model(agent_id)
        with self.cost_tracker.exclusive():
            request_id = self.cost_tracker.reserve(agent_id,model,amount,self.experiment_id,
                self.experiment_limit,self.agents[agent_id].get('daily_budget_usd',0))
            try:
                url = (self.base_url.removesuffix('/api/v1')+'/api/alpha/decisions'
                       if endpoint == 'decisions' else self.base_url+'/'+endpoint)
                response = self._client.post(url,
                    headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},json=payload)
                response.raise_for_status()
                data = response.json()
                usage = data.get('usage',{})
                entry = self.cost_tracker.log_call(agent_id,model,usage.get('prompt_tokens',usage.get('input_tokens',0)),
                    usage.get('completion_tokens',usage.get('output_tokens',0)),
                    endpoint,request_id=request_id,experiment_id=self.experiment_id,
                    provider_cost=usage.get('cost'),usage=usage,reservation=float(amount))
                self.last_cost_entry = entry
                if entry.state == 'unresolved':
                    raise UnresolvedCost('Provider cost unavailable; reservation retained')
                self.price_snapshot[model]['remaining'] -= Decimal(str(entry.cost_usd))
                if Decimal(str(entry.cost_usd)) > amount:
                    # Block subsequent calls if the provider exceeded the conservative bound.
                    self.cost_tracker._append({**asdict(entry),'state':'unresolved','error':'reservation_exceeded'})
                    raise UnresolvedCost('Actual cost exceeded reservation; spending stopped')
                return data
            except Exception as exc:
                latest = next(e for e in self.cost_tracker.effective_entries() if e.get('request_id')==request_id)
                if latest.get('state') == 'reserved':
                    self.cost_tracker.log_call(agent_id,model,0,0,endpoint,False,type(exc).__name__,
                        request_id=request_id,experiment_id=self.experiment_id,reservation=float(amount))
                raise

    def chat(self, agent_id, messages, max_tokens=None, temperature=0.7):
        maximum = max_tokens if max_tokens is not None else self.agents[agent_id].get('max_tokens_per_call',4096)
        if maximum <= 0:
            raise ValueError('Positive max_tokens required')
        payload = {'model':self._get_model(agent_id),'messages':messages,'max_tokens':maximum,
                   'temperature':temperature,'provider':{'allow_fallbacks':False}}
        data = self._request(agent_id,payload,'chat/completions')
        return data['choices'][0]['message']['content']

    def embed(self, texts, agent_id='embedding'):
        data = self._request(agent_id,{'model':self._get_model(agent_id),'input':texts},'embeddings')
        return [item['embedding'] for item in data['data']]

    def decide(self, agent_id, state, questions):
        """Experimental Decisions API; does not replace chat or scientific gates."""
        if self._get_model(agent_id) != 'typesafe/jev-1.13':
            raise ValueError('Pilot decisions are pinned to typesafe/jev-1.13')
        return self._request(agent_id,{'model':self._get_model(agent_id),
            'state':state,'questions':questions,
            'provider':{'only':['typesafe'],'allow_fallbacks':False}},'decisions')

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.close()
