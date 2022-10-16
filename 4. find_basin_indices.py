import subprocess
import os
import json
import numpy as np
import geopandas as gpd
from osgeo import osr, gdal

from postgresql import PostgreSQL

# parameters init
SNOWMELT_TYPE = 'MODIS'

if SNOWMELT_TYPE == 'PERSIANN':
    gt = (-180, .04, 0, 60, 0, -.04)
elif SNOWMELT_TYPE == 'MODIS':
    gt = (-180, .10, 0, 60, 0, -.10)


tmp_folder = f"tmp/{SNOWMELT_TYPE}"
EPSG = 4326

try:
    os.makedirs(tmp_folder)
except OSError:
    pass

#nc_file = os.path.join('classification', 'data', SNOWMELT_TYPE, '1hr_sum_2018.nc')
# set up path of netcdf file
nc_file = os.path.join('data', SNOWMELT_TYPE, '1hr_sum_2010.nc')
nc_ds = gdal.Open(nc_file)
xsize = nc_ds.RasterXSize
ysize = nc_ds.RasterYSize

tif_file = os.path.join(tmp_folder, 'raster.tif')
shp_file = os.path.join(tmp_folder, 'raster.shp')

# check if paths are existed
if not os.path.exists(tif_file):
    driver = gdal.GetDriverByName('GTiff')

    ds = driver.Create(
        tif_file,
        xsize,
        ysize,
        1,
        gdal.GDT_Int32
    )

    array = np.arange(ysize * xsize).reshape((ysize, xsize))

    ds.SetGeoTransform(gt)
    ds.GetRasterBand(1).WriteArray(array)
    source = osr.SpatialReference()
    source.ImportFromEPSG(EPSG)
    ds.SetProjection(source.ExportToWkt())
    ds = None

if not os.path.exists(shp_file):
    subprocess.call(
        #r"python C:\Users\jadeb\Anaconda3\Scripts\gdal_polygonize.py" + f" {tif_file} {shp_file}",
        r"python D:\Python36\Lib\site-packages\osgeo\scripts\gdal_polygonize.py" + f" {tif_file} {shp_file}",
        shell=True
    )

# database instance
pg = PostgreSQL('classification_snowmelt')

if not pg.table_exists(f'{SNOWMELT_TYPE.lower()}_raster'):
    # reading shape files
    gdf = gpd.GeoDataFrame.from_file(shp_file)
    print('finished reading file')

    def x():
        for _ in range(ysize):
            for j in range(xsize):
                yield j

    def y():
        for i in range(ysize):
            for _ in range(xsize):
                yield i

    xi = x()
    yi = y()

    def get_x(DM):
        return next(xi)

    def get_y(DM):
        return next(yi)

    gdf['x'] = gdf['DN'].apply(get_x)
    print('finished x')
    gdf['y'] = gdf['DN'].apply(get_y)
    print('finished y')

    gdf = gdf.drop('DN', axis=1)
    # create table to save geo data
    pg.cur.execute(f"""
        CREATE TABLE {SNOWMELT_TYPE.lower()}_raster (
            geom GEOMETRY(Polygon, 4326),
            x INT,
            y INT
        )
    """)

    n = len(gdf)

    data = []
    for i, row in gdf.iterrows():
        data.append((row['geometry'].wkt, row['x'], row['y']))
        
        if not i % 1000:
            print(f"{i}/{n}")
            # insert data
            pg.execute_values(
                "INSERT INTO " + SNOWMELT_TYPE.lower() + "_raster (geom, x, y) VALUES %s",
                data,
                template="(ST_SetSRID(ST_GeomFromText(%s), 4326), %s, %s)",
                page_size=1000
            )
            data = []
    # insert data
    pg.execute_values(
        "INSERT INTO " + SNOWMELT_TYPE.lower() + "_raster (geom, x, y) VALUES %s",
        data,
        template="(ST_SetSRID(ST_GeomFromText(%s), 4326), %s, %s)",
        page_size=1000
    )

    pg.cur.execute(f"""CREATE INDEX cell_idx_{SNOWMELT_TYPE.lower()}_raster ON {SNOWMELT_TYPE.lower()}_raster USING GIST (geom)""")
    pg.conn.commit()


if not pg.table_exists(f'{SNOWMELT_TYPE.lower()}_basin_indices'):
    # create table
    pg.cur.execute(f"""
        CREATE TABLE {SNOWMELT_TYPE.lower()}_basin_indices (
            idx VARCHAR PRIMARY KEY,
            indices JSONB
        )
    """)

    # find data from table subbasins_9
    pg.cur.execute("""
        SELECT id FROM subbasins_9
    """)

    res = pg.cur.fetchall()

    n_basins = len(res)

    for i, (basin, ) in enumerate(res):
        if not i % 100:
            print(f"{i}/{n_basins}")
            pg.conn.commit()

        # select data from combined subbasins_9 and raster table
        pg.cur.execute("""
            SELECT
                ST_Area(ST_Intersection(r.geom, s.geom), true),
                ST_Area(r.geom, true),
                r.x,
                r.y
            FROM  """ + SNOWMELT_TYPE.lower() + """_raster r, subbasins_9 s
            WHERE ST_Intersects(r.geom, s.geom)
            AND s.id = %s
        """, (basin, ))

        basin_overlaps = [
            {
                'x': res[2],
                'y': res[3],
                'area_basin': res[0],
                'area_cell': res[1]
            }
            for res in pg.cur.fetchall()
        ]

        # insert data
        pg.cur.execute("""
            INSERT INTO """ + SNOWMELT_TYPE.lower() + """_basin_indices (idx, indices)
            VALUES (%s, %s)
        """, (basin, json.dumps(basin_overlaps)))

    pg.conn.commit()
