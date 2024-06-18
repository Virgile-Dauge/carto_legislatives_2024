
#!/usr/bin/env python3
"""
This script contains asynchronous functions to load and save geospatial data
for different departments and elections.
"""

import asyncio

import pandas as pd
import geopandas as gpd

from pandas import DataFrame
from geopandas import GeoDataFrame

from folium import Map

from pathlib import Path
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