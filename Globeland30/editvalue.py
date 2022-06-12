# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-24 16:38:41
# @Desc  : 由于在globeland30_2020中，上海北部存在大片区域异常的分类为人造地表，因此需要对这部分地区进行修改。

from osgeo import gdal,gdalconst
import numpy as np
import os

'''4km文件的修改过程
origin_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\4km_globeland30_2020_lat40lon120.tif"
edt_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\mod4km_globeland30_2020_lat40lon120.tif"

origin_tiff: gdal.Dataset=gdal.Open(origin_file,gdalconst.GA_ReadOnly)
origin_band: gdal.Band=origin_tiff.GetRasterBand(1)
value=origin_band.ReadAsArray()
# 循环修改值
slice_value=value[216:219,46:55]
slice_value[np.where(slice_value==13)]=12
slice_value[np.where(slice_value==21)]=17
value[216:219,46:55]=slice_value
# 写入新文件
driver = gdal.GetDriverByName("GTiff")
edt_tiff: gdal.Dataset = driver.Create(edt_file, xsize=origin_tiff.RasterXSize, ysize=origin_tiff.RasterYSize,
                                       bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
edt_band: gdal.Band = edt_tiff.GetRasterBand(1)
edt_tiff.SetProjection(origin_tiff.GetProjection())
edt_tiff.SetGeoTransform(origin_tiff.GetGeoTransform())
edt_band.WriteArray(value)
edt_band.SetNoDataValue(0)
edt_tiff.FlushCache()
edt_tiff.GetRasterBand(1).ComputeStatistics(True)
'''

origin_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\100m_globeland30_2020_lat40lon120.tif"
edt_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\mod100m_globeland30_2020_lat40lon120.tif"

origin_tiff: gdal.Dataset=gdal.Open(origin_file,gdalconst.GA_ReadOnly)
origin_band: gdal.Band=origin_tiff.GetRasterBand(1)
value=origin_band.ReadAsArray()
# 循环修改值
# 1
slice_value=value[8638:8650,1871:2200]
slice_value[np.where(slice_value==13)]=12
slice_value[np.where(slice_value==21)]=12
value[8638:8650,1871:2200]=slice_value
# 2
slice_value=value[8650:8680,1870:2200]
slice_value[np.where(slice_value==13)]=12
slice_value[np.where(slice_value==21)]=12
value[8650:8680,1870:2200]=slice_value
# 3
slice_value=value[8680:8740,1855:2200]
slice_value[np.where(slice_value==13)]=12
slice_value[np.where(slice_value==21)]=12
value[8680:8740,1855:2200]=slice_value
# 写入新文件
driver = gdal.GetDriverByName("GTiff")
edt_tiff: gdal.Dataset = driver.Create(edt_file, xsize=origin_tiff.RasterXSize, ysize=origin_tiff.RasterYSize,
                                       bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
edt_band: gdal.Band = edt_tiff.GetRasterBand(1)
edt_tiff.SetProjection(origin_tiff.GetProjection())
edt_tiff.SetGeoTransform(origin_tiff.GetGeoTransform())
edt_band.WriteArray(value)
edt_band.SetNoDataValue(0)
edt_tiff.FlushCache()
edt_tiff.GetRasterBand(1).ComputeStatistics(True)