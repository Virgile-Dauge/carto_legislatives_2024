
#!/usr/bin/env python3
"""
This script contains asynchronous functions to load and save geospatial data
for different departments and elections.
"""

import asyncio
import aiofiles
import pandas as pd
import geopandas as gpd

from pandas import DataFrame
from geopandas import GeoDataFrame

from folium import Map

from pathlib import Path

import brotli

# Asynchronous function to compress file using Brotli with the best compression quality
async def compress_file_async(input_file_path: Path, output : Path | None=None):
    if output is None:
        output_file_path = input_file_path.with_suffix(input_file_path.suffix + '.br')
    else:
        default_dir = Path('./compressed_maps')
        default_dir.mkdir(parents=True, exist_ok=True)
        output_file_path = default_dir / input_file_path.name
    # Read the input file content asynchronously
    async with aiofiles.open(input_file_path, 'rb') as input_file:
        file_content = await input_file.read()
    
    # Compress the content using Brotli with the highest compression level (11)
    compressed_content = brotli.compress(file_content, quality=11)
    
    # Write the compressed content to the output file asynchronously
    async with aiofiles.open(output_file_path, 'wb') as output_file:
        await output_file.write(compressed_content)
    
    print(f'Compressed {input_file_path} to {output_file_path}')

async def load_geodata_async(dep_dir : Path, dep: int) -> tuple[GeoDataFrame, GeoDataFrame]:
    bv_gdf = await asyncio.to_thread(gpd.read_file, dep_dir / Path(f'bureaux_votes_{dep}.gpkg'))
    ci_gdf = await asyncio.to_thread(gpd.read_file, dep_dir / Path(f'circonscriptions_{dep}.gpkg'))
    return bv_gdf.rename(columns={'bureau': 'bv_id'}), ci_gdf

async def load_data_async(dep_dir : Path, election : str, dep: int) -> tuple[DataFrame, DataFrame]:
    bv_df = await asyncio.to_thread(pd.read_excel, dep_dir / Path(f'{election}_bureaux_votes_{dep}.xlsx'))
    ci_df = await asyncio.to_thread(pd.read_excel, dep_dir / Path(f'{election}_circonscriptions_{dep}.xlsx'))
    return bv_df, ci_df

async def save_map_async(map_obj : Map, file_path: Path) -> None:
    await asyncio.to_thread(map_obj.save, file_path)
    #await compress_file_async(file_path)
