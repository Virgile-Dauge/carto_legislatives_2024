import sys
from pathlib import Path

# Add the src directory to the sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import asyncio
import argparse

from pathlib import Path
from carto_legislatives_2024.utils_io import load_data_async, load_geodata_async, save_map_async
from carto_legislatives_2024.features import compute_feature, compute_features
from carto_legislatives_2024.gen_map import create_map

from shapely.geometry import Polygon

async def process_department(dep: str, election : str):
    print(f'Processing {dep}...')
    print('Loading files...')
    input_dir = Path(f'./départements/{dep}')
    bv_gdf, ci_gdf = await load_geodata_async(input_dir, dep)

    print('Computing features...')
    bv_gdf['Où parler aux électeurices du RN'] = compute_feature(bv_gdf, ci_gdf, 1, 6, 2, 6)
    bv_gdf['Où toucher les abstentionnistes'] = compute_feature(bv_gdf, ci_gdf, 6, 1, 2, 3)
    #final_gdf = compute_features(bv_gdf, ci_gdf)
    print('Creating map...')
    m = create_map(bv_gdf, ci_gdf)
    print('Saving files...')
    #output_dir = Path(f'./départements/{dep}')
    output_dir = Path(f'./maps/{dep}')
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

    semaphore = asyncio.Semaphore(4)  # Limit to 5 concurrent tasks

    async def sem_task(dep):
        async with semaphore:
            await process_department(dep, 'euro24')

    tasks = [sem_task(dep) for dep in departments]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())