from glob import glob
import pandas as pd
import xarray as xr

import matplotlib.pyplot as plt

fns = glob('input/trmm_3a12/3A12*.nc4')
ds = xr.open_mfdataset('input/trmm_3a12/3A12*.nc4', concat_dim='time')
ds['time'] = pd.to_datetime([fn.split('.')[1] for fn in fns])

ds.loc[dict(nlon=slice(115, 120), nlat=slice(10, 20))].groupby(ds['time'].dt.month)

df = ds.loc[dict(nlon=slice(115, 120), nlat=slice(10, 20))].groupby(ds['time'].dt.month).mean(['time', 'nlon', 'nlat']).to_dataframe()

df.loc[(1,), ['cldWater', 'rainWater', 'cldIce', 'snow', 'graupel']]

df.loc[(1,), ['rainWater', 'cldIce', 'snow', 'graupel']]


cld_wat_scl = [1, 0.01, 0.01, 0.01, 0.01, 1, 1, 1, 1, 0.25, 0.25, 0.25, 0.01]
rain_wat_scl = [1, 0.2, 0.2, 0.2, 0.2, 1, 1, 1, 1, 0.5, 0.5, 0.5, 0.2]

for m in range(1, 13):
    fig, ax = plt.subplots()
    plt_df = df.loc[(m,), ['cldWater', 'rainWater', 'cldIce', 'snow', 'graupel']].copy()
    plt_df['cldWater'] = plt_df['cldWater'] * cld_wat_scl[m]
    plt_df['rainWater'] = plt_df['rainWater'] * rain_wat_scl[m]

    g_df = plt_df.T.stack().rename_axis(['type','height']).to_frame('val').reset_index().groupby('type')

    for n, g in g_df:
        lab = n
        if lab=='cldWater':
            if cld_wat_scl[m] != 1:
                lab = '{} x{}'.format(n, cld_wat_scl[m])
        if lab=='rainWater':
            if rain_wat_scl[m] != 1:
                lab = '{} x{}'.format(n, rain_wat_scl[m])
                
        g.plot(x='val', y='height', label=lab, ax=ax)

    ax.set_xlabel('g/m^3')
    ax.set_ylabel('height (km)')
    plt.savefig('output/img/hydromet_mon/{}.png'.format(m))
    plt.close()