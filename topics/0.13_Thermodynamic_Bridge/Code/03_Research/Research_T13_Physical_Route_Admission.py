"""Selected native-MIMO route audit; no experimental-response fit or UET promotion."""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import io
import json
from pathlib import Path
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT))
from docs.scripts.audit.audit_calculation_completeness import artifact_metadata,load_json

SOURCE="docs/topics/0.13_Thermodynamic_Bridge/Data/03_Research/physical_route_admission_sources.json"
CONTRACT="docs/topics/0.13_Thermodynamic_Bridge/calculation_contracts/physical_route_admission.json"
OUTPUT="docs/core/07_artifacts/topic13/t13_physical_route_admission.json"


def voltage_harmonics(dc,ac):
    return dc*dc+ac*ac/2, 2*dc*ac, ac*ac/2


def gap_enclosure(amplitude):
    if not 0 <= amplitude < 1:
        raise ValueError("need a declared normalized amplitude below the gap")
    return 1/(1+amplitude)**2,1/(1-amplitude)**2


def dc_state(params,voltage,steps=48):
    """Conditional E1-off, zero-AC equilibrium on the declared small branch.

    Exact residual: wn2^2*y+k32*y^3-beta2*Vdc2^2/(1-y)^2.
    Certified uniqueness is ONLY on [0,1/4], not all equilibria.
    """
    wn,k,d,a,b=(Q(params[k]) for k in ("wn2","k32","delta2","alpha1","beta2"))
    if min(wn,b) <= 0 or min(k,d,a) < 0 or not 1 <= steps <= 64:
        raise ValueError("invalid source-model domain or unbounded job")
    forcing=b*voltage**2
    lo,hi=Q(0),Q(1,4)
    f=lambda y:wn**2*y+k*y**3-forcing/(1-y)**2
    derivative_lower=wn**2-2*forcing/(1-hi)**3
    if derivative_lower<=0 or f(lo)>0 or f(hi)<0:
        raise ValueError("declared stable branch not certified; no clipped fallback")
    if f(lo)==0:
        hi=lo
    else:
        for _ in range(steps):
            mid=(lo+hi)/2
            if f(mid)<0:
                lo=mid
            else:
                hi=mid
    kl=wn**2+3*k*lo**2-2*forcing/(1-hi)**3
    kh=wn**2+3*k*hi**2-2*forcing/(1-lo)**3
    ml,mh=1+d*lo**2,1+d*hi**2
    if kl<=0:
        raise ValueError("unresolved local stability")
    r2l,r2h=kl/mh/(1+a*hi),kh/ml/(1+a*lo)
    return {"y_interval":[lo,hi],"frequency_ratio_squared_interval":[r2l,r2h],
            "auxiliary_frequency_squared_interval":[kl/mh,kh/ml],
            "monotonicity_lower_bound":derivative_lower,"root_width":hi-lo}


def serial_state(state):
    return {k:([str(x) for x in v] if isinstance(v,list) else str(v)) for k,v in state.items()}


def verify_supplement(source):
    """Explicit optional public-reference check; no download stored on disk."""
    reference=source["supplement"]
    expected="https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-022-14657-1/MediaObjects/41598_2022_14657_MOESM1_ESM.docx"
    if reference["url"]!=expected:
        raise ValueError("unexpected reference URL")
    with urllib.request.urlopen(expected,timeout=25) as response:
        data=response.read(8_000_001)
    if len(data)>8_000_000 or len(data)!=reference["bytes"] or hashlib.sha256(data).hexdigest()!=reference["sha256"]:
        raise ValueError("remote identity mismatch; source review required")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        info=z.getinfo("word/document.xml")
        if info.file_size>5_000_000:
            raise ValueError("oversized XML")
        root=ET.fromstring(z.read(info))
    ns={"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    table=root.find(".//w:tbl",ns)
    rows={}
    for row in table.findall("w:tr",ns):
        cells=["".join(c.itertext()).strip().replace("µ","μ") for c in row.findall("w:tc",ns)]
        if len(cells)==2:
            rows[cells[0]]=cells[1].replace("−","-").replace("×10","e")
    labels={"k31":"k31","k32":"k32","alpha1":"α1","alpha2":"α2","beta1":"β1","beta2":"β2",
            "delta1":"δ1","delta2":"δ2","mu1":"μ1","mu2":"μ2","wn2":"ωn2"}
    for key,label in labels.items():
        if Q(rows[label])!=Q(reference["table_s1_model_values"][key]):
            raise ValueError(f"table transcription mismatch: {key}")
    return {"remote_sha256_verified":True,"table_values_verified":len(labels),"raw_file_stored":False}


def calculate(source):
    params=source["supplement"]["table_s1_model_values"]
    state=dc_state(params,Q(source["diagnostic_plan"]["bias_V"]),source["diagnostic_plan"]["bisection_steps"])
    zero=dc_state(params,Q(0))
    assert state["root_width"]<=Q(1,2**50)
    assert state["auxiliary_frequency_squared_interval"][1] < zero["auxiliary_frequency_squared_interval"][0]
    dc=Q(source["reference_protocol"]["Vdc2_V"])
    ac=Q(source["reference_protocol"]["Vac2_peak_V"])
    _,fundamental,second=voltage_harmonics(dc,ac)
    unmet=[p for p in source["admission_prerequisites"] if p["status"]!="ADMITTED"]
    if not unmet:
        raise ValueError("admission state changed; freeze a new physical protocol before scoring")
    return {"route_status":"SELECTED_NATIVE_MIMO_ROUTE_NOT_ADMITTED_FOR_UET_TEST",
            "selected_route":source["selected_route"],"selection_reason":source["selection_reason"],
            "alternatives":[s for s in source["sources"] if s["id"]!="USHAPE_2022"],
            "native_operator_difference":["gap-dependent squared-voltage sources","nonlinear inertial terms","bias-dependent equilibrium and local mass/stiffness","damping and coordinate/readout normalization"],
            "configured_model_diagnostic":serial_state(state),"zero_bias_model_diagnostic":serial_state(zero),
            "fixed_coordinate_second_to_first_voltage_square_ratio":str(second/fundamental),
            "ratio_boundary":"Source-equation algebra only, not a measured total-force contamination bound under moving gap",
            "direct_auxiliary_drive_boundary":"Published high-mode drive is not source-free auxiliary response of the inherited low-mode cubic-kernel protocol",
            "inertia_identity":"u*u_dot^2+u^2*u_ddot=-(A^3*Omega^2/2)*(cos(theta)+cos(3theta)) for u=A*cos(theta)",
            "authors_sensitivity_boundary":source["supplement"]["sensitivity_boundary"],
            "calibration_origin":source["supplement"]["parameter_origin"],
            "unmet_prerequisites":unmet,"data_access_boundary":source["bounded_locator_check"],
            "physical_acceptance":False,"experimental_rows_scored":0,"new_UET_terms":0,
            "decision":"Current inputs support a route-specific limitation and exact missing packet, not locked physical UET prediction",
            "next_input":"Verified native normalization plus independently calibrated same-state source/readout/error records and a derived or bounded UET-to-native operator map"}


def record():
    metadata=artifact_metadata(load_json(ROOT/CONTRACT),ROOT)
    return {**calculate(load_json(ROOT/SOURCE)),**metadata,
            "generator_path":Path(__file__).relative_to(ROOT).as_posix(),
            "evidence_class":"SOURCE_MODEL_DIAGNOSTIC_AND_PHYSICAL_ROUTE_LIMITATION"}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--emit",action="store_true")
    mode.add_argument("--verify-supplement",action="store_true")
    args=p.parse_args()
    if args.verify_supplement:
        print(json.dumps(verify_supplement(load_json(ROOT/SOURCE))))
        return
    content=json.dumps(record(),ensure_ascii=False,indent=2,allow_nan=False)+"\n"
    path=ROOT/OUTPUT
    if args.emit:
        if shutil.disk_usage(ROOT).free<100*1024*1024:
            raise SystemExit("Insufficient disk space")
        path.write_text(content,encoding="utf-8",newline="\n")
    elif not path.exists() or path.read_text(encoding="utf-8")!=content:
        raise SystemExit("Missing/drifted evidence; --check does not write")
    print("SELECTED_NATIVE_MIMO_ROUTE_NOT_ADMITTED_FOR_UET_TEST; no physical scoring")


if __name__=="__main__":
    main()
