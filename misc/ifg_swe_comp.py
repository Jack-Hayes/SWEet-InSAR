import glob
import os
import pandas as pd
import xarray as xr
import h5py
import numpy as np
from tqdm import tqdm
import geopandas as gpd
import easysnowdata as esd
import sys
sys.path.append('/home/jehayes/sh_final/SWEet-InSAR/misc')
from unwrap import unwrap_phase_fft

WAVELENGTH = 0.056
inc_angle_deg = 35
SNTL_CODES = [
    '589_CO_SNTL', '1185_CO_SNTL', '465_CO_SNTL',
    '586_CO_SNTL', '629_CO_SNTL', '713_CO_SNTL', '538_CO_SNTL'
]
SNOTEL_GEOJSON_URL = "https://github.com/egagli/snotel_ccss_stations/raw/main/all_stations.geojson"
OUTPUT_DIR = '/home/jehayes/sh_final/SWEet-InSAR/data'

def process_pairs(files, sntl_codes, gf_snotel_co, direction_label):
    results = []
    for i in tqdm(range(len(files) - 1), desc=f"Processing {direction_label} pairs"):
        fn_1 = files[i]
        fn_2 = files[i + 1]

        dsR = xr.open_dataset(fn_1,
                        group='data',
                        engine='h5netcdf')['VV'].rename(dict(x_coordinates='x', y_coordinates='y'))
        tR = pd.to_datetime(xr.open_dataset(fn_1, 
                                            group='identification')['zero_doppler_start_time'].data.astype('U'))
        dsS = xr.open_dataset(fn_2,
                            group='data',
                            engine='h5netcdf')['VV'].rename(dict(x_coordinates='x', y_coordinates='y'))
        tS = pd.to_datetime(xr.open_dataset(fn_2, group='identification')['zero_doppler_start_time'].data.astype('U'))
        ifg = dsR * np.conj(dsS)
        ifg.attrs['reference'] = tR
        ifg.attrs['secondary'] = tS
        da = xr.apply_ufunc(np.angle, ifg)
        ds = da.to_dataset(name='phase')
        ds.rio.write_crs('EPSG:32613', inplace=True)
        with h5py.File(fn_2, 'r') as f:
            crs = f['/metadata/noise_information/projection'][()] 
        np_wrapped_phase = ds.phase.values
        np_unwrapped = unwrap_phase_fft(np_wrapped_phase)
        da_unwrapped = xr.DataArray(np_unwrapped, 
                                    dims=ds.phase.dims, 
                                    coords=ds.phase.coords).rio.write_crs(crs)
        da_unwrapped = da_unwrapped.where(~np.isnan(ds.phase))
        with h5py.File(fn_2, 'r') as f:
            wavelength = f['metadata']['processing_information']['input_burst_metadata']['wavelength'][()]
        da_displacement = da_unwrapped * (wavelength / (4 * np.pi))
        inc_angle_rad = np.deg2rad(inc_angle_deg)
        da_displacement_vert = da_displacement / np.cos(inc_angle_rad)

        # Process SNOTEL data
        results.extend(process_snotel_data(sntl_codes, gf_snotel_co, tR, tS, da_displacement_vert))

        # Save DataFrame
        df_swe = pd.DataFrame(results)
        output_filename = os.path.join(OUTPUT_DIR, f"{tR.date()}_{tS.date()}_{direction_label}_swe_disp.parquet")
        df_swe.to_parquet(output_filename)

def process_snotel_data(sntl_codes, gf_snotel_co, tR, tS, da_displacement):
    results = []
    for code in sntl_codes:
        snotel = esd.automatic_weather_stations.StationCollection()
        snotel.get_data(code)
        df_snotel = snotel.data

        swe_reference = df_snotel.loc[tR.date(), "WTEQ"] if tR.date() in df_snotel.index else np.nan
        swe_secondary = df_snotel.loc[tS.date(), "WTEQ"] if tS.date() in df_snotel.index else np.nan
        swe_diff = swe_secondary - swe_reference

        snotel_point = gf_snotel_co.loc[gf_snotel_co['code'] == code, 'geometry'].item()
        insar_vert_disp = da_displacement.interp(x=snotel_point.x, y=snotel_point.y, method="linear").item()

        results.append({
            'sntl_code': code,
            'reference_date': tR.date(),
            'secondary_date': tS.date(),
            'insar_vert_disp': insar_vert_disp,
            'swe_diff': swe_diff
        })
    return results

def main():
    # Load SNOTEL stations data
    gf_snotel = gpd.read_file(SNOTEL_GEOJSON_URL).set_index("code")
    gf_snotel_co = gf_snotel[gf_snotel.index.isin(SNTL_CODES)].reset_index()

    # Process descending data
    desc_files = sorted(glob.glob('/home/jehayes/sh_final/cslc/desc/*.h5'))
    process_pairs(desc_files, SNTL_CODES, gf_snotel_co, 'desc')

    # Process ascending data
    asc_files = sorted(glob.glob('/home/jehayes/sh_final/cslc/asc/*.h5'))
    process_pairs(asc_files, SNTL_CODES, gf_snotel_co, 'asc')

if __name__ == "__main__":
    main()
