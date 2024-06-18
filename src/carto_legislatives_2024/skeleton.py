import sys
from pathlib import Path

# Add the src directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio
import argparse

from pathlib import Path
from carto_legislatives_2024.utils_io import load_data_async, load_geodata_async, save_map_async
from carto_legislatives_2024.features import compute_features
from carto_legislatives_2024.gen_map import create_map

from shapely.geometry import Polygon

async def process_department(dep: str, election : str):
    print(f'Processing {dep}...')
    print('Loading files...')
    input_dir = Path(f'./départements/{dep}')
    bv_gdf, ci_gdf = await load_geodata_async(input_dir, dep)
    bv_df, ci_df = await load_data_async(input_dir, election, dep)
    print('Computing features...')
    
    ci_df['ci_id'] = ci_df['ci_id'].astype(str).str.strip()
    ci_gdf['ci_id'] = ci_gdf['ci_id'].astype(str).str.strip()
    merged_ci = ci_gdf.merge(ci_df, on='ci_id')

    bv_df['bv_id'] = bv_df['bv_id'].astype(str)
    bv_gdf['bv_id'] = bv_gdf['bv_id'].astype(str)
    merged_bv = bv_gdf.merge(bv_df, on='bv_id')
    merged_ci.geometry = merged_ci.geometry.make_valid()
    merged_bv.geometry = merged_bv.geometry.make_valid()
    

    def convert_to_polygon(geometry):
        if geometry.geom_type == 'Polygon':
            return geometry
        elif geometry.geom_type == 'MultiPolygon':
            # Return the largest polygon by area
            return geometry
            #return max(geometry, key=lambda a: a.area)
        elif geometry.geom_type == 'GeometryCollection':
            # Extract polygons from GeometryCollection
            polygons = [geom for geom in geometry.geoms if isinstance(geom, Polygon)]
            if polygons:
                return max(polygons, key=lambda a: a.area)
        return None
    merged_bv['geometry'] = merged_bv['geometry'].apply(convert_to_polygon)
    
    final_gdf = compute_features(merged_bv, merged_ci)
    print('Creating map...')
    m = create_map(final_gdf, merged_ci)
    print('Saving files...')
    output_dir = Path(f'./départements/{dep}')
    output_dir.mkdir(parents=True, exist_ok=True)
    await save_map_async(m, output_dir / Path(f'analyse_{election}_{dep}.html'))


async def main():
    parser = argparse.ArgumentParser(description='Process department data.')
    parser.add_argument('-d', '--departments', type=int, nargs='*', help='List of department numbers')
    args = parser.parse_args()

    if args.departments:
        departments = args.departments
    else:
        departments = [d.name for d in Path('./départements').iterdir() if d.is_dir() and d.name.isdigit()]

    tasks = [process_department(dep, 'euro24') for dep in departments]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())