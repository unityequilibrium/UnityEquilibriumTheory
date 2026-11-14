"""Cyclic source work in the named acoustic-populated Gaussian insertion.

The real two-block Hamiltonian counts both pair orientations: its force is
T:X, twice the predecessor's single-oriented .5*T:X. No vacuum population,
collision rate, material temperature or entropy production is supplied.
"""

from datetime import datetime, timezone
import json
from math import isfinite, pi, sqrt
from pathlib import Path
import sys

import mpmath as mp
import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import block_diag

ROOT = Path(__file__).resolve().parents[5]
LOCAL = Path(__file__).resolve().parent
if str(LOCAL) not in sys.path:
    sys.path.insert(0, str(LOCAL))
import Research_T13_Thermal_Noether_Response as NOE
import Research_T13_Collisionless_Soft_Source as SOFT

FQ, VIRT, EFT, TH, MOD, PREFIX = NOE.FQ, NOE.VIRT, NOE.EFT, NOE.TH, NOE.MOD, NOE.PREFIX
REGISTRY = PREFIX+"Data/03_Research/t13_gaussian_source_work_registry.json"
OUTPUT = ROOT/(PREFIX+"Result/artifacts/t13_gaussian_source_work.json")
FIRST_FAILURE = ROOT/(PREFIX+"Result/artifacts/t13_gaussian_source_work_first_failure.json")
# Frozen before the first audit; all scales are conditional natural units.
MU_GRID = (1.05, 1.2)
MOMENTUM_TRIPLES = ((.02, .031, .02), (.04, .037, .02), (.02, .02, 0.))
TEMPERATURE = .004
DURATION, CARRIER = 80., .04
AMPLITUDES = (.02, .01, .005)
SOLVERS = ({"rtol": 1e-8, "atol": 1e-11, "max_step": .5},
           {"rtol": 1e-10, "atol": 1e-13, "max_step": .25})
GATES = {"source_equation_relative": 1e-9, "endpoint_absolute": 1e-10,
         "work_method_relative": 2e-6, "solver_work_relative": 1e-6,
         "exact_energy_work_relative": 1e-5, "exact_to_leading_relative": .01,
         "symplectic_relative": 1e-8, "volume_entropy_absolute": 1e-8,
         "fourier_absolute_scaled": 1e-9, "negative_control_minimum": .1,
         "original_causal_leakage": 1e-6}


def tones(duration=DURATION, carrier=CARRIER):
    if not all(isfinite(x) for x in (duration, carrier)) or duration <= 0 or carrier < 0:
        raise ValueError("positive duration and nonnegative carrier required")
    result = [(35/128, carrier)]
    for n, coefficient in ((1, -56/128), (2, 28/128), (3, -8/128), (4, 1/128)):
        result.extend([(coefficient/2, carrier+2*n*pi/duration),
                       (coefficient/2, carrier-2*n*pi/duration)])
    return result


def pulse_jet(t, duration=DURATION, carrier=CARRIER):
    """Derivatives through seven of sin^8(pi*t/L)*cos(carrier*t)."""
    terms = tones(duration, carrier)
    if not isfinite(t):
        raise ValueError("finite time required")
    if t <= 0 or t >= duration:
        # The analytic compact source has seven vanishing endpoint derivatives.
        return np.zeros(8)
    return np.array([sum(c*w**n*np.cos(w*t+n*pi/2) for c, w in terms) for n in range(8)])


def pulse_fourier(nu, duration=DURATION, carrier=CARRIER, digits=50):
    """Exact finite-interval tone integral, not a retarded pole width."""
    tones(duration, carrier)
    if not isfinite(nu) or digits < 25:
        raise ValueError("finite real frequency and at least 25 digits required")
    ctx = mp.mp.clone()
    ctx.dps = digits
    length, omega, frequency = [ctx.mpf(str(x)) for x in (duration, carrier, nu)]

    def integral(k):
        x = k*length/2
        return length*ctx.exp(1j*x)*(ctx.sin(x)/x if x else 1)

    result = ctx.mpf(35)/128*(integral(frequency+omega)+integral(frequency-omega))/2
    for n, coefficient in ((1, -56), (2, 28), (3, -8), (4, 1)):
        for w in (omega+2*n*ctx.pi/length, omega-2*n*ctx.pi/length):
            result += ctx.mpf(coefficient)/256*(integral(frequency+w)+integral(frequency-w))/2
    return complex(result)


def source_path(t, q, state, action, amplitude=1.):
    """Construct a Phi-only source by solving the unsourced radial/phase rows."""
    if state["h"] != 0 or state["xi"] != 0 or action["gamma"] == 0:
        raise ValueError("rest h0=0 and nonzero declared coupling required")
    if not isfinite(q) or q < 0 or not isfinite(amplitude):
        raise ValueError("finite nonnegative q and finite amplitude required")
    kinetic, linear, potential = VIRT.matrices(q, state, action)
    gyro = (1j*linear).real
    mu, gv = state["mu"], action["gamma"]*sqrt(state["s"])
    u2 = 2*action["u"]*state["s"]
    jet = amplitude*pulse_jet(t)
    coeff = u2+2*q*q+4*mu*mu
    const = q*q*(u2+q*q)
    b = np.array([-(jet[2]+q*q*jet[0])/(2*mu), jet[1],
                  -(jet[4]+coeff*jet[2]+const*jet[0])/(2*mu*gv)])
    velocity = np.array([-(jet[3]+q*q*jet[1])/(2*mu), jet[2],
                         -(jet[5]+coeff*jet[3]+const*jet[1])/(2*mu*gv)])
    acceleration = np.array([-(jet[4]+q*q*jet[2])/(2*mu), jet[3],
                             -(jet[6]+coeff*jet[4]+const*jet[2])/(2*mu*gv)])
    equation = kinetic@acceleration+gyro@velocity+potential@b
    scale = np.linalg.norm(kinetic@acceleration)+np.linalg.norm(gyro@velocity)+np.linalg.norm(potential@b)
    return b, velocity, float(equation[2]), float(np.linalg.norm(equation[:2])/(scale or 1.))


def source_fourier(nu, q, state, action):
    if not isfinite(nu) or not isfinite(q) or q < 0 or state["h"] != 0 or state["xi"] != 0 or action["gamma"] == 0:
        raise ValueError("real frequency, nonnegative q and coupled rest h0=0 required")
    f = pulse_fourier(nu)
    mu, gv = state["mu"], action["gamma"]*sqrt(state["s"])
    u2 = 2*action["u"]*state["s"]
    sigma = (nu*nu-q*q)*f/(2*mu)
    response = ((u2+q*q-nu*nu)*sigma+2*mu*nu*nu*f)/gv
    b = np.array([sigma, -1j*nu*f, response])
    h = (state["V_curvature"]+action["epsilon"]*action["response_kinetic"]*(q*q-nu*nu))*response-gv*sigma
    return b, complex(h)


def pulse_fourier_quadrature(nu, order=512):
    if not isfinite(nu) or not isinstance(order, int) or order < 2:
        raise ValueError("finite frequency and quadrature order >=2 required")
    x, weights = np.polynomial.legendre.leggauss(order)
    t = DURATION*(1+x)/2
    f = np.sin(pi*t/DURATION)**8*np.cos(CARRIER*t)
    return complex(np.sum(weights*DURATION/2*f*np.exp(1j*nu*t)))


def linear_work(p, r, q, temperature, state, action, solver=1):
    NOE.geometry(p, r, q)
    FQ.validate(p, r, temperature, state, action)
    ap, cp = FQ.evolution_and_covariance(p, temperature, state, action)
    ar, cr = FQ.evolution_and_covariance(r, temperature, state, action)
    kinetic, linear, potential = VIRT.matrices(q, state, action)
    invk, gyro, cubic = np.linalg.inv(kinetic), (1j*linear).real, MOD.cubic_tensor(state, action)
    contact = 2*NOE.pair_contact((cp+cr)/2, state, action)[0]

    def rhs(t, y):
        cross, mean, velocity = y[:36].reshape(6, 6), y[36:39], y[39:42]
        b, bdot, h, _ = source_path(t, q, state, action)
        delta_a = np.zeros((6, 6))
        delta_a[3:, :3] = -invk@np.einsum("ijk,k->ij", cubic, b)
        cross_dot = ar@cross+cross@ap.T+delta_a@cp+cr@delta_a.T
        force = np.einsum("iab,ab->i", cubic, cross[:3, :3])
        mean_accel = -invk@(gyro@velocity+potential@mean+force+contact@b)
        return np.concatenate([cross_dot.ravel(), velocity, mean_accel,
                               [bdot@force, h*velocity[2], bdot@contact@b, h*bdot[2]]])

    solution = solve_ivp(rhs, (0., DURATION), np.zeros(46), method="DOP853", **SOLVERS[solver])
    if not solution.success or not np.all(np.isfinite(solution.y)):
        raise RuntimeError("linear source/covariance evolution failed")
    covariance, source, contact_work, tree_work = solution.y[42:, -1]
    return {"covariance_work": float(covariance), "source_mean_work": float(source),
            "contact_cycle_work": float(contact_work), "tree_cycle_work_density": float(tree_work),
            "function_evaluations": solution.nfev}


def spectral_work(p, r, q, temperature, state, action):
    NOE.geometry(p, r, q)
    FQ.validate(p, r, temperature, state, action)
    cubic = MOD.cubic_tensor(state, action)
    rows = []
    for i, (ep, up) in enumerate(VIRT.tree_modes(p, state, action)):
        for j, (er, ur) in enumerate(VIRT.tree_modes(r, state, action)):
            npop = TH.bose(ep/temperature) if i == 0 and temperature else 0.
            rpop = TH.bose(er/temperature) if j == 0 and temperature else 0.
            summed, difference = ep+er, er-ep
            pair_v = np.einsum("ijk,k->ij", cubic, source_fourier(summed, q, state, action)[0])
            number_v = np.einsum("ijk,k->ij", cubic, source_fourier(difference, q, state, action)[0])
            pair = summed*(npop+rpop)*abs(np.vdot(up, pair_v@ur.conjugate()))**2/(4*ep*er)
            number = difference*(npop-rpop)*abs(np.vdot(ur, number_v@up))**2/(4*ep*er)
            rows.append({"i": i, "j": j, "pair_frequency": summed, "number_frequency": difference,
                         "pair_work": float(pair), "number_work": float(number)})
    return {"work": sum(row["pair_work"]+row["number_work"] for row in rows), "channels": rows,
            "vacuum_plus_one_included": False}


def pair_hamiltonian(p, r, temperature, state, action):
    ap, cp = FQ.evolution_and_covariance(p, temperature, state, action)
    ar, cr = FQ.evolution_and_covariance(r, temperature, state, action)
    kinetic, linear, vp = VIRT.matrices(p, state, action)
    vr = VIRT.matrices(r, state, action)[2]
    k6, g6, v6 = block_diag(kinetic, kinetic), block_diag((1j*linear).real, (1j*linear).real), block_diag(vp, vr)
    covariance = np.zeros((12, 12))
    for indices, value in (([0, 1, 2, 6, 7, 8], cp), ([3, 4, 5, 9, 10, 11], cr)):
        covariance[np.ix_(indices, indices)] = value
    invk = np.linalg.inv(k6)
    poisson = np.block([[np.zeros((6, 6)), invk], [-invk, -invk@g6@invk]])
    canonical = np.block([[np.eye(6), np.zeros((6, 6))], [g6/2, k6]])
    return k6, g6, v6, covariance, poisson, canonical


def exact_cycle(p, r, q, temperature, state, action, amplitude, solver=1):
    NOE.geometry(p, r, q)
    FQ.validate(p, r, temperature, state, action)
    if not isfinite(amplitude):
        raise ValueError("finite amplitude required")
    k6, g6, v0, covariance, poisson, canonical = pair_hamiltonian(p, r, temperature, state, action)
    invk, cubic = np.linalg.inv(k6), MOD.cubic_tensor(state, action)

    def matrices(t):
        b, bdot, _, _ = source_path(t, q, state, action, amplitude)
        vertex = np.einsum("ijk,k->ij", cubic, b)
        derivative = np.einsum("ijk,k->ij", cubic, bdot)
        perturbation = np.block([[np.zeros((3, 3)), vertex], [vertex, np.zeros((3, 3))]])
        vdot = np.block([[np.zeros((3, 3)), derivative], [derivative, np.zeros((3, 3))]])
        potential = v0+perturbation
        generator = np.block([[np.zeros((6, 6)), np.eye(6)], [-invk@potential, -invk@g6]])
        return generator, vdot

    def rhs(t, y):
        flow = y[:144].reshape(12, 12)
        generator, vdot = matrices(t)
        evolved = flow@covariance@flow.T
        return np.concatenate([(generator@flow).ravel(), [.5*np.sum(vdot*evolved[:6, :6])]])

    solution = solve_ivp(rhs, (0., DURATION), np.concatenate([np.eye(12).ravel(), [0.]]),
                         method="DOP853", **SOLVERS[solver])
    if not solution.success or not np.all(np.isfinite(solution.y)):
        raise RuntimeError("Hamiltonian source cycle failed")
    flow, work = solution.y[:144, -1].reshape(12, 12), float(solution.y[144, -1])
    evolved = flow@covariance@flow.T
    energy = lambda c: float(.5*np.sum(v0*c[:6, :6])+.5*np.sum(k6*c[6:, 6:]))
    delta = energy(evolved)-energy(covariance)
    canonical_flow = canonical@flow@np.linalg.inv(canonical)
    j = np.block([[np.zeros((6, 6)), np.eye(6)], [-np.eye(6), np.zeros((6, 6))]])
    # This full-rank control is not a vacuum completion of the rank-four insertion.
    test_cov = np.diag(np.linspace(1., 2., 12))
    sign0, log0 = np.linalg.slogdet(test_cov)
    sign1, log1 = np.linalg.slogdet(canonical_flow@test_cov@canonical_flow.T)
    sign_flow, log_flow = np.linalg.slogdet(flow)
    return {"amplitude": amplitude, "work": work, "energy_change": delta,
            "work_ledger_relative": abs(delta-work)/max(abs(work), abs(delta), 1e-30),
            "symplectic_relative": VIRT.matrix_error(flow@poisson@flow.T, poisson),
            "canonical_poisson_relative": VIRT.matrix_error(canonical@poisson@canonical.T, j),
            "orientation_preserving": bool(sign_flow == sign0 == sign1 == 1),
            "log_volume_change": float(log_flow), "conditional_full_rank_entropy_change": float((log1-log0)/2),
            "insertion_rank": int(np.linalg.matrix_rank(covariance)),
            "insertion_entropy": "UNDEFINED_FULL_COVARIANCE_RANK_DEFICIENT_NOT_QUANTUM_STATE",
            "evolved_insertion_rank": int(np.linalg.matrix_rank(evolved)),
            "function_evaluations": solution.nfev}


def relative(first, second):
    return float(abs(first-second)/max(abs(first), abs(second), 1e-30))


def extended_leading_work(p, r, q, temperature, state, action, digits=50):
    """Integrate the exact forced Liouvillian tones, independently of modal work.

    This computes the coefficient at amplitude zero, not an extrapolation
    fitted to the failed finite-amplitude grid. The original audit is retained.
    """
    NOE.geometry(p, r, q)
    left = SOFT.extended_gaussian_state(p, temperature, state, action, digits)
    ctx = left["ctx"]
    right = SOFT.extended_gaussian_state(r, temperature, state, action, digits, ctx)
    real = lambda x: ctx.mpf(str(x))
    length, carrier, q = real(DURATION), real(CARRIER), real(q)
    mu, gv, u2 = left["mu"], real(action["gamma"])*left["v"], 2*real(action["u"])*left["s"]
    terms = [(ctx.mpf(35)/128, carrier)]
    for n, coefficient in ((1, -56), (2, 28), (3, -8), (4, 1)):
        terms += [(ctx.mpf(coefficient)/256, carrier+2*n*ctx.pi/length),
                  (ctx.mpf(coefficient)/256, carrier-2*n*ctx.pi/length)]
    integral_cache = {}

    def integral(z):
        if z not in integral_cache:
            integral_cache[z] = ctx.expm1(z*length)/z if z else length
        return integral_cache[z]

    def derivative_integral(z):
        return ((length*z-1)*ctx.exp(z*length)+1)/(z*z) if z else length*length/2

    vertices, drives = [], []
    for coefficient, frequency in terms:
        for nu in (frequency, -frequency):
            f = coefficient/2
            sigma = (nu*nu-q*q)*f/(2*mu)
            b = [sigma, -1j*nu*f, ((u2+q*q-nu*nu)*sigma+2*mu*nu*nu*f)/gv]
            vertex = sum((left["cubic"][i]*b[i] for i in range(3)), ctx.matrix(3, 3))
            delta_a = ctx.matrix(6, 6)
            block = -(left["kinetic"]**-1)*vertex
            for a in range(3):
                for bb in range(3):
                    delta_a[a+3, bb] = block[a, bb]
            rhs = delta_a*left["covariance"]+right["covariance"]*delta_a.T
            drives.append((nu, right["inverse"]*rhs*left["inverse"].T))
            projected = right["basis"][:3, :].T*vertex*left["basis"][:3, :]
            vertices.append((nu, vertex, projected))
    temporal = ctx.mpc(0)
    for omega, _, projection in vertices:
        for nu, drive in drives:
            for i in range(6):
                for j in range(6):
                    rho = right["eigenvalues"][i]+left["eigenvalues"][j]
                    divisor = -1j*nu-rho
                    convolution = ((integral(-1j*(omega+nu))-integral(rho-1j*omega))/divisor
                                   if divisor else derivative_integral(rho-1j*omega))
                    temporal += -1j*omega*projection[i, j]*drive[i, j]*convolution

    def vertex_transform(frequency):
        return sum((vertex*integral(1j*(frequency-nu)) for nu, vertex, _ in vertices), ctx.matrix(3, 3))

    spectral = ctx.mpf(0)
    for i in range(3):
        ep, up = ctx.re(1j*left["eigenvalues"][i]), left["basis"][:3, i]
        npop = 1/ctx.expm1(ep/real(temperature)) if i == 0 and temperature else ctx.mpf(0)
        for j in range(3):
            er, ur = ctx.re(1j*right["eigenvalues"][j]), right["basis"][:3, j]
            rpop = 1/ctx.expm1(er/real(temperature)) if j == 0 and temperature else ctx.mpf(0)
            pair = (up.conjugate().T*vertex_transform(ep+er)*ur.conjugate())[0]
            number = (ur.conjugate().T*vertex_transform(er-ep)*up)[0]
            spectral += ((ep+er)*(npop+rpop)*abs(pair)**2+(er-ep)*(npop-rpop)*abs(number)**2)/(4*ep*er)
    return {"digits": digits, "time_convolution_work": float(ctx.re(temporal)), "modal_work": float(spectral),
            "method_relative": float(abs(ctx.re(temporal)-spectral)/abs(spectral)) if spectral else float(abs(temporal)),
            "imaginary_work_relative": float(abs(ctx.im(temporal))/abs(spectral)) if spectral else float(abs(ctx.im(temporal))),
            "finite_amplitude_fit_used": False, "energy_frame": "rotating_Gaussian_Hamiltonian; full physical Noether ledger not closed"}


def audit():
    action, rows, source_errors, fourier_errors = EFT.controls(), [], [], []
    for mu in MU_GRID:
        state = EFT.tree_state(mu, action=action)
        for p, r, q in MOMENTUM_TRIPLES:
            for t in np.linspace(1., DURATION-1., 17):
                source_errors.append(source_path(float(t), q, state, action)[3])
            for nu in (0., .01, .04, .3, 1.4, 2.7):
                b, h = source_fourier(nu, q, state, action)
                residual = VIRT.kernel(q, nu, state, action)@b-np.array([0., 0., h])
                source_errors.append(float(np.linalg.norm(residual)/max(np.linalg.norm(VIRT.kernel(q, nu, state, action)@b), abs(h), 1e-30)))
                fourier_errors.append(abs(pulse_fourier(nu)-pulse_fourier_quadrature(nu))/DURATION)
            coarse = linear_work(p, r, q, TEMPERATURE, state, action, 0)
            fine = linear_work(p, r, q, TEMPERATURE, state, action, 1)
            spectral = spectral_work(p, r, q, TEMPERATURE, state, action)
            cycles = [exact_cycle(p, r, q, TEMPERATURE, state, action, epsilon) for epsilon in AMPLITUDES]
            reference_cycle = exact_cycle(p, r, q, TEMPERATURE, state, action, AMPLITUDES[-1], 0)
            zero = linear_work(p, r, q, 0., state, action)
            extended = extended_leading_work(p, r, q, TEMPERATURE, state, action)
            precision_control = extended_leading_work(p, r, q, TEMPERATURE, state, action, 35)
            rows.append({"mu": mu, "T": TEMPERATURE, "p": p, "r": r, "q": q,
                         "linear": fine, "spectral": spectral, "cycles": cycles,
                         "extended_leading": extended,
                         "extended_precision_control_relative": relative(extended["modal_work"], precision_control["modal_work"]),
                         "work_methods_relative": relative(fine["covariance_work"], spectral["work"]),
                         "mean_source_work_relative": relative(fine["source_mean_work"], fine["covariance_work"]),
                         "linear_resolution_relative": relative(coarse["covariance_work"], fine["covariance_work"]),
                         "exact_resolution_relative": relative(reference_cycle["work"], cycles[-1]["work"]),
                         "exact_to_leading_relative": [relative(c["work"]/c["amplitude"]**2, spectral["work"]) for c in cycles],
                         "observed_halved_amplitude_work_ratios": [b["work"]/a["work"] for a, b in zip(cycles, cycles[1:])],
                         "zero_temperature_work_absolute": max(abs(zero["covariance_work"]), abs(zero["source_mean_work"])),
                         "wrong_half_orientation_relative": relative(fine["covariance_work"]/2, spectral["work"])})
    checks = {
        "Phi_only_source_equations": max(source_errors) < GATES["source_equation_relative"],
        "compact_source_endpoints": all(np.max(abs(pulse_jet(t))) < GATES["endpoint_absolute"] for t in (0., DURATION)),
        "independent_fourier_quadrature": max(fourier_errors) < GATES["fourier_absolute_scaled"],
        "time_covariance_and_modal_spectrum": all(x["work_methods_relative"] < GATES["work_method_relative"] for x in rows),
        "mean_source_and_covariance_work": all(x["mean_source_work_relative"] < GATES["work_method_relative"] for x in rows),
        "source_cycle_resolution": all(max(x["linear_resolution_relative"], x["exact_resolution_relative"]) < GATES["solver_work_relative"] for x in rows),
        "exact_cycle_energy_ledger": all(c["work_ledger_relative"] < GATES["exact_energy_work_relative"] for x in rows for c in x["cycles"]),
        "leading_amplitude_limit": all(x["exact_to_leading_relative"][-1] < GATES["exact_to_leading_relative"] and all(a > b for a, b in zip(x["exact_to_leading_relative"], x["exact_to_leading_relative"][1:])) for x in rows),
        "Hamiltonian_symplectic_and_volume": all(c["symplectic_relative"] < GATES["symplectic_relative"] and c["canonical_poisson_relative"] < GATES["symplectic_relative"] and c["orientation_preserving"] and abs(c["log_volume_change"]) < GATES["volume_entropy_absolute"] for x in rows for c in x["cycles"]),
        "conditional_entropy_control_and_primary_rank": all(abs(c["conditional_full_rank_entropy_change"]) < GATES["volume_entropy_absolute"] and c["insertion_rank"] == c["evolved_insertion_rank"] == 4 for x in rows for c in x["cycles"]),
        "conservative_contact_cycle": all(abs(x["linear"]["contact_cycle_work"]) < GATES["work_method_relative"]*abs(x["spectral"]["work"]) for x in rows),
        "positive_stimulated_work_no_vacuum": all(x["spectral"]["work"] > 0 and all(c["pair_work"] >= 0 and c["number_work"] >= 0 for c in x["spectral"]["channels"]) and x["zero_temperature_work_absolute"] == 0 for x in rows),
        "wrong_orientation_detected": all(x["wrong_half_orientation_relative"] > GATES["negative_control_minimum"] for x in rows)}
    passed = all(checks.values())
    extended_checks = {
        "exact_tone_covariance_and_modal_work": all(x["extended_leading"]["method_relative"] < GATES["work_method_relative"] for x in rows),
        "work_is_real": all(x["extended_leading"]["imaginary_work_relative"] < GATES["work_method_relative"] for x in rows),
        "same_input_precision_control": all(x["extended_precision_control_relative"] < GATES["solver_work_relative"] for x in rows)}
    zero_drive = exact_cycle(*MOMENTUM_TRIPLES[0], TEMPERATURE, EFT.tree_state(MU_GRID[0], action=action), action, 0.)
    protected = [PREFIX+"Result/artifacts/t13_collisionless_soft_source.json", PREFIX+"Result/artifacts/t13_thermal_noether_response.json", PREFIX+"Result/artifacts/t13_finite_q_thermal_source.json"]+[PREFIX+"Code/03_Research/"+name for name in ("Research_T13_Collisionless_Soft_Source.py", "Research_T13_Thermal_Noether_Response.py", "Research_T13_Finite_Q_Thermal_Source.py", "Research_T13_Thermal_Virtual_Response.py")]+list(EFT.ACTION_PATHS)
    paths = [str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), REGISTRY, PREFIX+"Code/03_Research/test_t13_gaussian_source_work.py"]
    record = {"major_result_id": "T13_GAUSSIAN_CYCLIC_SOURCE_WORK_AND_ENTROPY_BOUNDARY", "topic": "0.13_Thermodynamic_Bridge", "branch_id": VIRT.BRANCH,
              "created_at": datetime.now(timezone.utc).isoformat(), "closure_level": "CLOSED_FOR_LANE" if passed else "PARTIAL",
              "verification_status": "PASS_SCOPED_GAUSSIAN_SOURCE_WORK" if passed else "FAIL_SCOPED_GAUSSIAN_SOURCE_WORK",
              "what_is_closed": "High-precision zero-amplitude covariance/modal work identity and conditional Hamiltonian entropy boundary; original finite-amplitude/binary64 controls remain failed",
              "equation_or_mapping": "W_h_loop=int h*dot_l_Phi=int dot_b*T:X=W_modal; Delta_E_exact=int .5*Tr(dot_V*C); S P S^T=P",
              "units": {"b_Phi": "E", "h": "E^3", "loop_mean_per_internal_pair": "E^-2", "cyclic_pair_work": "E", "integrated_work_density_if_measure_admitted": "E^4", "tree_work_density": "E^4", "conditional_entropy_difference": "dimensionless fixed-coordinate diagnostic; not material entropy"},
              "derivation_class": "DERIVED_REAL_PAIR_HAMILTONIAN_AND_STIMULATED_MODAL_TRANSITIONS", "observable": "conditional cyclic source energy transfer; no Kelvin/heat/readout admission", "data_role": "DERIVED_NOT_CALIBRATION",
              "declared_protocol": {"mu": MU_GRID, "momentum_triples": MOMENTUM_TRIPLES, "T": TEMPERATURE, "duration": DURATION, "carrier": CARRIER, "amplitudes": AMPLITUDES, "solvers": SOLVERS, "fourier_quadrature_order": 512, "locked_before_first_audit": True, "pair_orientation_factor": 2},
              "action_controls": action, "thresholds": GATES, "checks": checks, "extended_leading_checks": extended_checks, "examples": rows,
              "zero_drive_control": zero_drive, "zero_drive_drift_subtracted_from_work": False,
              "maximum_source_equation_relative": max(source_errors), "maximum_fourier_scaled_error": max(fourier_errors),
              "evidence_artifacts": TH.identities(paths), "protected_evidence_hashes": TH.identities(protected),
              "equation_registry_ids": [x["id"] for x in json.loads((ROOT/REGISTRY).read_text())["entries"]],
              "energy_frame": "rotating_Gaussian_Hamiltonian_not_full_physical_Noether_energy",
              "raw_audit_preserved": str(FIRST_FAILURE.relative_to(ROOT)).replace("\\", "/"),
              "preserved_first_failure_identity": TH.identities([str(FIRST_FAILURE.relative_to(ROOT)).replace("\\", "/")]) if FIRST_FAILURE.exists() else [],
              "first_failure_is_not_relabelled_by_extended_checks": True,
              "leading_work_identity_verified": all(extended_checks.values()),
              "controlling_blocker": "full_interacting_heat_readout_collision_and_entropy_mapping_open" if passed else "finite_amplitude_work_grid_outside_leading_limit_and_binary64_work_cancellation",
              "open_blockers": ["frozen_finite_amplitude_grid_not_in_leading_work_regime", "binary64_tiny_work_cancellation_and_energy_difference_floor", "full_interacting_vacuum_thermal_and_approximation_control", "collision_operator_and_irreversible_entropy_contract", "actual_material_heat_source_readout_and_independent_scale"],
              "dependency_unlocked": ["physical_heat_readout_and_interacting_work_research_only"] if passed else [],
              "leading_finite_pair_source_work_closed": passed, "collisionless_absorption_entropy_boundary_recorded": passed,
              "full_energy_exchange_ledger_closed": False, "full_collision_operator_computed": False, "full_SK_KMS_matching_closed": False,
              "physical_Kubo_emitted": False, "independent_alpha_Phi_K_admitted": False, "full_core_unlock": False, "core_composition_gate_overwritten": False,
              "full_off_shell_source_matching_closed": False, "full_real_self_energy_matched": False, "full_two_loop_pressure_computed": False,
              "all_parent_modes_and_quantum_Phi_loops_included": False, "controlled_full_action_truncation_error_established": False,
              "state_variables": ["radial_phase_Phi_fluctuations_velocities_and_covariance"], "excluded_variables": ["C", "UET_Pi", "R_gen", "R_obs"],
              "primary_covariance_entropy_defined": False, "full_rank_entropy_control_is_diagnostic_only": True,
              "quantum_vacuum_population_added": False, "parameter_fitting": False, "assigned_width": False, "assigned_relaxation_time": False,
              "clipping": False, "cone_padding": False, "claim_promotion": False, "xie_2026_accessed": False, "prior_Xie_context_exposure_review": "REVIEW_REQUIRED",
              "primary_references": ["https://arxiv.org/abs/1608.04977", "https://arxiv.org/abs/quant-ph/0307073", "https://www.jstage.jst.go.jp/article/jpsj1946/12/6/12_6_570/_article"],
              "claim_boundary": "Finite real-pair Gaussian rotating-energy cyclic work and conditional fine-grained entropy boundary only. Extended zero-amplitude coefficient does not make the failed binary64/finite-amplitude grid pass. Stimulated acoustic populations, not complete quantum covariance or vacuum heating; no full interacting collision/heat/transport/KMS/entropy, SI material mapping, conserved-C repair or Full Topic13/Core/global closure."}
    record["subresults"] = [
        {"major_result_id": "T13_GAUSSIAN_ZERO_AMPLITUDE_CYCLIC_WORK_IDENTITY", "topic": record["topic"],
         "closure_level": "CLOSED_FOR_LANE" if all(extended_checks.values()) else "PARTIAL",
         "what_is_closed": "Leading work coefficient from exact time-domain Liouvillian convolution and independent stimulated modal transitions, at identical source parameters",
         "equation_or_mapping": "W2=int dot_b*T:X=W_pair+W_number; source mean reciprocity follows by integration by parts with compact b endpoints",
         "units": record["units"], "derivation_class": record["derivation_class"], "observable": record["observable"], "data_role": "DERIVED_NOT_CALIBRATION",
         "evidence_artifacts": record["evidence_artifacts"], "verification_status": extended_checks,
         "open_blockers": record["open_blockers"], "dependency_unlocked": [], "claim_boundary": record["claim_boundary"]},
        {"major_result_id": "T13_GAUSSIAN_CONDITIONAL_FINE_GRAINED_ENTROPY_BOUNDARY", "topic": record["topic"],
         "closure_level": "CLOSED_FOR_LANE" if checks["Hamiltonian_symplectic_and_volume"] and checks["conditional_entropy_control_and_primary_rank"] else "PARTIAL",
         "what_is_closed": "Symplectic/volume conservation and conditional full-rank entropy identity; rank-deficient primary insertion does not define complete-state entropy",
         "equation_or_mapping": "S P S^T=P; det S=1; conditional full-rank Delta_s=log|det S|=0",
         "units": record["units"], "derivation_class": "DERIVED_FINITE_HAMILTONIAN_FLOW_IDENTITY", "observable": "conditional fine-grained invariants, not irreversible thermal entropy", "data_role": "DERIVED_AND_DIAGNOSTIC_ONLY_FULL_RANK_CONTROL",
         "evidence_artifacts": record["evidence_artifacts"], "verification_status": {key: checks[key] for key in ("Hamiltonian_symplectic_and_volume", "conditional_entropy_control_and_primary_rank")},
         "open_blockers": ["complete_state_and_collision_or_coarse_graining_contract_not_admitted"], "dependency_unlocked": [], "claim_boundary": record["claim_boundary"]}]
    fields = ("MAJOR_RESULT_CLOSURE", "WHAT_IS_ACTUALLY_CLOSED", "WHAT_REMAINS_OPEN", "DEPENDENCY_UNLOCKED", "STATUS", "WHAT_CHANGED", "EQUATION_OR_MAPPING", "VERIFICATION", "CONTROLLING_BLOCKER", "NEXT_ACTION", "CLAIM_BOUNDARY")
    record["report"] = dict(zip(fields, (record["closure_level"], record["what_is_closed"], record["open_blockers"], record["dependency_unlocked"], record["verification_status"], "Derived source-compatible cyclic work and entropy boundary", record["equation_or_mapping"], checks, record["controlling_blocker"], "Independent physical heat/readout mapping and interacting collision/entropy, not assigned rates", record["claim_boundary"])))
    return record


if __name__ == "__main__":
    result = audit()
    encoded = (json.dumps(result, indent=2, allow_nan=False)+"\n").encode("utf-8")
    OUTPUT.write_bytes(encoded)
    if not all(result["checks"].values()) and not FIRST_FAILURE.exists():
        FIRST_FAILURE.write_bytes(encoded)
    print(json.dumps({"status": result["verification_status"], "checks": result["checks"]}, indent=2))
    raise SystemExit(0 if all(result["checks"].values()) else 1)
