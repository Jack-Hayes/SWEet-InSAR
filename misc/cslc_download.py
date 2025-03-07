import asf_search
import geopandas as gpd
from shapely.geometry import box

def fetch_and_download(parms, path):
    burst_hits = asf_search.search(**parms)
    all_urls = [item.properties['url'] for item in burst_hits]
    asf_search.download_urls(urls=all_urls, path=path)

def main():
    gf_snotel = gpd.read_file(
        "https://github.com/egagli/snotel_ccss_stations/raw/main/all_stations.geojson"
    ).set_index("code")
    gf_snotel = gf_snotel[gf_snotel.network == "SNOTEL"].reset_index()

    sntl_codes = [
        '589_CO_SNTL', '1185_CO_SNTL', '465_CO_SNTL',
        '586_CO_SNTL', '629_CO_SNTL', 
    ]
    gf_snotel_co_4326 = gf_snotel[gf_snotel.code.isin(sntl_codes)]

    bounds = gf_snotel_co_4326.total_bounds
    gf_search = gpd.GeoDataFrame(
        geometry=[box(bounds[0], bounds[1], bounds[2], bounds[3])],
        crs="EPSG:4326"
    )
    wkt_search = gf_search.geometry.to_wkt().iloc[0]

    date_ranges = [
        ('2019-01-01T00:00:00Z', '2019-03-31T00:00:00Z'),
        ('2020-01-01T00:00:00Z', '2020-03-31T00:00:00Z'),
        ('2021-01-01T00:00:00Z', '2021-03-31T00:00:00Z'),
        ('2022-01-01T00:00:00Z', '2022-03-31T00:00:00Z'),
        ('2023-01-01T00:00:00Z', '2023-03-31T00:00:00Z'),
        ('2024-01-01T00:00:00Z', '2024-03-31T00:00:00Z')
    ]

    base_parms = {
        'dataset': asf_search.DATASET.OPERA_S1,
        'processingLevel': asf_search.PRODUCT_TYPE.CSLC,
        'intersectsWith': wkt_search,
        'operaBurstID': ['T049_103322_IW2', 'T129_275785_IW1'],
        'maxResults': 100,
    }

    for start, end in date_ranges:
        for direction, path in [('ASCENDING', '/home/jehayes/sh_final/cslc/asc'),
                                ('DESCENDING', '/home/jehayes/sh_final/cslc/desc')]:
            parms = base_parms.copy()
            parms.update({
                'start': start,
                'end': end,
                'flightDirection': getattr(asf_search.FLIGHT_DIRECTION, direction),
            })
            fetch_and_download(parms, path)

if __name__ == "__main__":
    main()