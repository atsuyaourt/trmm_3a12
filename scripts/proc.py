from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

in_dir = Path("input/trmm_3a12")
out_dir = Path("output/img/hydromet_mon")

out_dir.mkdir(parents=True, exist_ok=True)

nc_files = in_dir.glob("3A12*.nc4")
ds = xr.open_mfdataset("input/trmm_3a12/3A12*.nc4", combine="nested", concat_dim="time")
ds["time"] = pd.to_datetime([nc_file.name.split(".")[1] for nc_file in nc_files])

ds.loc[dict(nlon=slice(115, 120), nlat=slice(10, 20))].groupby(ds["time"].dt.month)

df = (
    ds.loc[dict(nlon=slice(115, 120), nlat=slice(10, 20))]
    .groupby(ds["time"].dt.month)
    .mean(["time", "nlon", "nlat"])
    .to_dataframe()
)

for m in range(1, 13):
    # plt_df = df.loc[(m,), ['cldWater', 'rainWater', 'cldIce', 'snow', 'graupel']].copy()
    plt_dfs = {
        "ice": {
            "df": df.loc[(m,), ["cldIce", "snow", "graupel"]].copy(),
            "xticks": np.linspace(0, 0.015, 11),
        },
        "water": {
            "df": df.loc[(m,), ["cldWater", "rainWater"]].copy(),
            "xticks": np.linspace(0, 0.08, 9),
        },
    }

    for plt_name, plt_df in plt_dfs.items():
        fig, ax = plt.subplots()
        g_df = (
            plt_df["df"]
            .T.stack()
            .rename_axis(["type", "height"])
            .to_frame("val")
            .reset_index()
            .groupby("type")
        )

        for n, g in g_df:
            lab = n
            g.plot(x="val", y="height", label=lab, ax=ax)

        ax.set_xticks(plt_df["xticks"])
        ax.set_xlabel("g/m^3")
        ax.set_ylabel("height (km)")
        plt.savefig(out_dir / f"hydromet_{plt_name}_{m:02d}.png")
        plt.close()
