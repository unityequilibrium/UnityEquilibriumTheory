// LocalRunner: deterministic, dependency-free functions (safe: no eval).
// Add new equations by adding pure functions here.

export class LocalRunner {
  async run(equationDef, params) {
    const fn = equationDef?.runner?.fn;
    if (!fn) throw new Error("EquationDef missing runner.fn");
    if (!(fn in FNS)) throw new Error(`Unknown local runner function: ${fn}`);
    return FNS[fn](params);
  }
}

function num(x, name) {
  const v = Number(x);
  if (!Number.isFinite(v)) throw new Error(`Invalid number for ${name}`);
  return v;
}

const FNS = {
  // V_C(C) = a C^2/2 + δ C^4/4 + s C
  vc_quartic_0d: ({ C, a, delta, s }) => {
    C = num(C,"C"); a = num(a,"a"); delta = num(delta,"delta"); s = num(s,"s");
    const V = (a*C*C)/2 + (delta*Math.pow(C,4))/4 + s*C;
    return { V };
  },

  // μ_C = dV/dC = a C + δ C^3 + s
  mu_c_0d: ({ C, a, delta, s }) => {
    C = num(C,"C"); a = num(a,"a"); delta = num(delta,"delta"); s = num(s,"s");
    const mu = a*C + delta*Math.pow(C,3) + s;
    return { mu };
  },

  // One Euler step: C_next = C - dt*M*μ
  c_euler_step_0d: ({ C, a, delta, s, M, dt }) => {
    C = num(C,"C"); a = num(a,"a"); delta = num(delta,"delta"); s = num(s,"s");
    M = num(M,"M"); dt = num(dt,"dt");
    const mu = a*C + delta*Math.pow(C,3) + s;
    const C_next = C - dt*M*mu;
    return { C_next, mu };
  }
};
