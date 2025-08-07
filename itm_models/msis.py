import numpy as np
import xarray as xr
import pymsis

def msis(time, lat, lon, alt, f107=None, f107a=None, ap=None, **kwargs):
    """
    Compute MSIS atmospheric parameters using pymsis, with support for both 
    gridded and flythrough modes.

    Parameters
    ----------
    time : array-like of datetime64 or pandas.Timestamp
        One or more time points for the calculation.
    lat : array-like
        Latitude(s) in degrees.
    lon : array-like
        Longitude(s) in degrees.
    alt : array-like
        Altitude(s) in km.

    f107 : float or array-like, optional
        Daily F10.7 solar flux. Can be a scalar or an array matching `time`.

    f107a : float or array-like, optional
        81-day averaged F10.7 solar flux. Can be a scalar or an array matching `time`.

    ap : float or array-like, optional
        Planetary geomagnetic index. Must be a scalar or array matching `time`.
        (Note: The storm-time 7-element Ap arrays are not currently supported.)

    kwargs : dict
        Additional keyword arguments passed to `pymsis.calculate()`.

    Returns
    -------
    xr.Dataset
        An xarray Dataset containing MSIS output variables. Dimensions are inferred 
        from the input shapes. Supports both 1D flythrough and N-D grid output.
    
    """
    
    t = np.atleast_1d(np.array(time, dtype="datetime64[ns]"))
    nt = len(t)
    
    lat = np.atleast_1d(lat)
    lon = np.atleast_1d(lon)
    alt = np.atleast_1d(alt)
    
    if f107 is not None and np.isscalar(f107):
        # Broadcast to len of t if needed.
        f107 = f107 * np.ones(len(t))
        
    if f107a is not None and np.isscalar(f107a):
        f107a = f107a * np.ones(len(t))

    if ap is not None and np.isscalar(ap):
        ap = ap * np.ones(len(t))
    if ap is not None:
        # Also adjust ap to the 7-element input that's needed by pymsis
        ap = [[a,0,0,0,0,0,0] for a in ap]

    
    result = pymsis.calculate(
        t,
        lon,
        lat,
        alt,
        f107s=f107,
        f107as=f107a,
        aps = ap,
        **kwargs
    )
    
    variables = pymsis.Variable
    
    if result.ndim == 5:
        ds =  xr.Dataset(
            {
                v.name: (("time", "lon", "lat", "alt"), result[:,:,:,:,i]) for i, v in enumerate(variables)
            },
            coords={
                "time": t,
                "alt": alt,
                "lat": lat,
                "lon": lon,
            },
        )
    
    elif result.ndim == 2:
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