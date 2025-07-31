import numpy as np
import xarray as xr
import pymsis

def msis(time, lat, lon, alt, f107=None, f107a=None, **kwargs):
    """
    Wrapper for pymsis.calculate() → xarray.Dataset.
    Supports grid and flythrough mode. Optional f107 inputs. (Ap is not yet implemented)
    """
    t = np.atleast_1d(np.array(time, dtype="datetime64[ns]"))
    nt = len(t)
    
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    alt = np.atleast_1d(alt)
    
    if f107 is not None and np.isscalar(f107):
        # Broadcast to shape of t if needed. Otherwise
        f107 = f107 * np.ones(len(t))
        
    if f107a is not None and np.isscalar(f107a):
        f107a = f107a * np.ones(len(t))
        
    
    result = pymsis.calculate(
        t,
        lat,
        lon,
        alt,
        f107s=f107,
        f107as=f107a,
        **kwargs
    )
    
    variables = pymsis.Variable
    
    if result.ndim == 5:
        # (var, time, alt, lat, lon)
        ds =  xr.Dataset(
            {
                v.name: (("time", "lat", "lon", "alt"), result[:,:,:,:,i]) for i, v in enumerate(variables)
            },
            coords={
                "time": t,
                "alt": alt,
                "lat": lat,
                "lon": lon,
            },
        )
    
    elif result.ndim == 2:
        # (var, time)
        ds = xr.Dataset(
            {
                v.name: (("time",), result[:,i]) for i, v in enumerate(variables)
            },
            coords={
                "time": t,
                "alt": alt,
                "lat": lat,
                "lon": lon,
            },
        )


    ds['MASS_DENSITY'].attrs['units'] = 'kg/m^3'
    for v in ['N2','O2','O','HE','H','AR','N','ANOMALOUS_O','NO']:
        ds[v].attrs['units'] = '1/m^3'
    ds['TEMPERATURE'].attrs['units'] = 'K'
    ds['alt'].attrs['units'] = 'km'
    ds['lat'].attrs['units'] = 'deg'
    ds['lon'].attrs['units'] = 'deg'
    
    return ds.squeeze(drop=False) # Don't keep dims that are only of length 1