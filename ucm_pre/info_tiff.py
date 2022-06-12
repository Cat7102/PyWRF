# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-04-05 03:39:18
# @Desc  : 读取tiff文件的信息

from osgeo import gdal, gdalconst, osr
import numpy as np

def gettiffinfo(filepath):
    tiff: gdal.Dataset=gdal.Open(filepath, gdalconst.GA_ReadOnly)
    print(gdal.Info(tiff))
    #srcSRS = osr.SpatialReference()
    #srcSRS.ImportFromWkt(tiff.GetProjection())
    #print(srcSRS.GetAttrValue("AUTHORITY", 1))
    #print(tiff.RasterXSize,tiff.RasterYSize)
    band: gdal.Band=tiff.GetRasterBand(1)
    array=band.ReadAsArray()
    #print(np.max(array))

if __name__ == '__main__':
    gettiffinfo(r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\resampled&reclassified_4km\reclassified_globeland30_2020_lat30lon70.tif")