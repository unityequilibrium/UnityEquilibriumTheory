"""Gate the source-of-funds and resource-to-output transaction lane.

The lane distinguishes revenue/profit, equity, debt, transfers and new
bank-credit money. It must not infer funding provenance from M2 alone.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/"Result/artifacts/0_25_funding_source_flow_gate.json"
def main():
 out={"schema_version":"1.0","topic":"0.25_Strategy_Power_Economics","status":"BLOCKED","flow_identity":{"funding_sources":["operating revenue","retained profit","equity issuance","bank/market debt","government transfers/subsidies","new bank credit/deposit creation"],"uses":["labor compensation","natural-resource extraction","intermediate inputs","capital formation","tax/interest/dividend payments","debt repayment"],"chain":"funding source -> payment -> labor/resource transformation -> output -> revenue -> distribution/repayment"},"required_sources":{"BEA":"Supply-Use/Input-Output and sectoral income/accounts","Federal Reserve Z.1":"sectoral financial assets/liabilities and funding flows","BLS":"hours, compensation, productivity and input-output labor detail","EIA/USGS/FAOSTAT":"resource extraction and physical throughput","Census":"firm revenue, costs, employment and capital formation"},"blockers":["No source-locked transaction-level or sectoral funding-flow panel links payer, funding source, resource extraction, labor input, and output.","M2 and aggregate debt cannot identify whether a payment came from profit, equity, debt, transfer, or newly created bank credit.","No reconciliation artifact closes the sectoral accounting identity across funding sources, uses, and repayments."],"claim_boundary":"The prior R/M mismatch is not a funding-provenance measure. No claim about money-backed resource transformation is permitted until this gate is PASS."};ART.write_text(json.dumps(out,indent=2)+"\n");print('Funding-source flow gate: BLOCKED')
if __name__=="__main__":main()
