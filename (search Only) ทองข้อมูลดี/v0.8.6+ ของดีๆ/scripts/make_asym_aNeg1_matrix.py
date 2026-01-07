import pandas as pd

src="matrices/UET_Param_CI_delta_asym_sweep.csv"
dst="matrices/UET_Param_CI_delta_asym_sweep_aNeg1.csv"

df=pd.read_csv(src)
df["params"]=df["params"].str.replace("quartic(a=1,", "quartic(a=-1,", regex=False)
df["tier"]="param_CI_asym_aNeg1"
df["case_id"]=df["case_id"].str.replace("param_CI_", "param_CI_aN1_", regex=False)

df.to_csv(dst, index=False)
print("ok", len(df), "->", dst)
