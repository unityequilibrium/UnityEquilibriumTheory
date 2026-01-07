import pandas as pd

src = "matrices/UET_Cross_CI_beta_s_sweep_seed10.csv"
dst = "matrices/UET_Cross_CI_beta_s_aNeg1_sweep_seed10.csv"

df = pd.read_csv(src)

# เปลี่ยน quartic(a=1,...) -> quartic(a=-1,...)
df["params"] = df["params"].str.replace("quartic(a=1,", "quartic(a=-1,", regex=False)

# เปลี่ยนชื่อเคส/เทียร์ กันสับสน
df["tier"] = "param_CI_betaXs_aNeg1"
df["case_id"] = df["case_id"].str.replace("param_CI_bs_", "param_CI_bs_aN1_", regex=False)

df.to_csv(dst, index=False)
print("ok", len(df), "->", dst)
