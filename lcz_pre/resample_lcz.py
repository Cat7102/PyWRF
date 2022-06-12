# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-03-26 01:28:26
# @Desc  : 将tiff文件重采样，可以提升或降低分辨率,专用于lcz
import numpy as np
from osgeo import gdal,gdalconst
import os,time

def resample_lcz(inputfile,outputfile,resolution,method,type,bound1=301387.5,bound2=3385582.5,bound3=423277.5,bound4=3531292.5,targetAlignedSign=True):
    start=time.time()
    tiff_data = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    print("开始转换：" + inputfile)
    gdal.Warp(outputfile, tiff_data, format='GTiff',
              xRes=resolution, yRes=resolution,
              outputBounds=[bound1,bound2,bound3,bound4],
              outputType=type, resampleAlg=method, targetAlignedPixels=targetAlignedSign,
              srcSRS='EPSG:32651', dstSRS='EPSG:32651')
    print("转换完成，耗时为：{}s".format(time.time()-start))
    print("开始优化")
    del tiff_data
    rewrite_tiff = gdal.Open(outputfile, gdalconst.GA_ReadOnly)
    retiff_width, retiff_height = rewrite_tiff.RasterXSize, rewrite_tiff.RasterYSize
    retiff_proj = rewrite_tiff.GetProjection()  # 得到数据集的投影信息
    retiff_geo = rewrite_tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
    retiff_band = rewrite_tiff.GetRasterBand(1)
    retiff_list = retiff_band.ReadAsArray()
    del rewrite_tiff
    driver = gdal.GetDriverByName('GTiff')
    tiff_new = driver.Create(outputfile, xsize=retiff_width, ysize=retiff_height,
                             bands=1, eType=type, options=["TILED=YES", "COMPRESS=LZW"])
    tiff_new.SetProjection(retiff_proj)  # SetProjection写入投影im_proj
    tiff_new.SetGeoTransform(retiff_geo)  # SetGeoTransform写入地理信息
    tiff_new.GetRasterBand(1).WriteArray(retiff_list)
    tiff_new.GetRasterBand(1).ComputeStatistics(True)   # 统计值
    tiff_new.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
    del tiff_new
    print("优化完成，耗时为：{}s".format(time.time() - start))

def resample_ndvi(inputfile,outputfile,resolution,method,type,raster_band,bound1=301387.5,bound2=3385582.5,bound3=423277.5,bound4=3531292.5):
    start=time.time()
    tiff_data = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    print("开始转换：" + inputfile)
    gdal.Warp(outputfile, tiff_data, format='GTiff',
              xRes=resolution, yRes=resolution,
              outputBounds=[bound1,bound2,bound3,bound4],
              outputType=type, resampleAlg=method, targetAlignedPixels=True,
              srcSRS='EPSG:32651', dstSRS='EPSG:32651')
    print("转换完成，耗时为：{}s".format(time.time()-start))
    print("开始优化")
    del tiff_data
    rewrite_tiff = gdal.Open(outputfile, gdalconst.GA_ReadOnly)
    retiff_width, retiff_height = rewrite_tiff.RasterXSize, rewrite_tiff.RasterYSize
    retiff_proj = rewrite_tiff.GetProjection()  # 得到数据集的投影信息
    retiff_geo = rewrite_tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
    retiff_band = rewrite_tiff.GetRasterBand(raster_band)
    retiff_list = retiff_band.ReadAsArray()
    del rewrite_tiff
    driver = gdal.GetDriverByName('GTiff')
    tiff_new = driver.Create(outputfile, xsize=retiff_width, ysize=retiff_height,
                             bands=1, eType=type, options=["TILED=YES", "COMPRESS=LZW"])
    tiff_new.SetProjection(retiff_proj)  # SetProjection写入投影im_proj
    tiff_new.SetGeoTransform(retiff_geo)  # SetGeoTransform写入地理信息
    tiff_new.GetRasterBand(1).WriteArray(retiff_list)
    tiff_new.GetRasterBand(1).WriteArray(retiff_list)
    tiff_new.GetRasterBand(1).ComputeStatistics(True)   # 统计值
    tiff_new.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
    del tiff_new
    print("优化完成，耗时为：{}s".format(time.time() - start))

def resample_pop(inputfile,outputfile,resolution,method,type,raster_band,bound1=301387.5,bound2=3385582.5,bound3=423277.5,bound4=3531292.5):
    start=time.time()
    tiff_data = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    print("开始转换：" + inputfile)
    gdal.Warp(outputfile, tiff_data, format='GTiff',
              xRes=resolution, yRes=resolution,
              outputBounds=[bound1,bound2,bound3,bound4],
              outputType=type, resampleAlg=method, targetAlignedPixels=False,
              srcSRS='EPSG:4326', dstSRS='EPSG:4326')
    print("转换完成，耗时为：{}s".format(time.time()-start))
    print("开始优化")
    del tiff_data
    rewrite_tiff = gdal.Open(outputfile, gdalconst.GA_ReadOnly)
    retiff_width, retiff_height = rewrite_tiff.RasterXSize, rewrite_tiff.RasterYSize
    retiff_proj = rewrite_tiff.GetProjection()  # 得到数据集的投影信息
    retiff_geo = rewrite_tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
    retiff_band = rewrite_tiff.GetRasterBand(raster_band)
    retiff_list = retiff_band.ReadAsArray()
    del rewrite_tiff
    driver = gdal.GetDriverByName('GTiff')
    tiff_new = driver.Create(outputfile, xsize=retiff_width, ysize=retiff_height,
                             bands=1, eType=type, options=["TILED=YES", "COMPRESS=LZW"])
    tiff_new.SetProjection(retiff_proj)  # SetProjection写入投影im_proj
    tiff_new.SetGeoTransform(retiff_geo)  # SetGeoTransform写入地理信息
    tiff_new.GetRasterBand(1).WriteArray(retiff_list)
    tiff_new.GetRasterBand(1).WriteArray(retiff_list)
    tiff_new.GetRasterBand(1).ComputeStatistics(True)   # 统计值
    tiff_new.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
    del tiff_new
    print("优化完成，耗时为：{}s".format(time.time() - start))

if __name__ == '__main__':
    resample_lcz(r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\4_LCZ_Shanghai\LCZC_v1.3.tif",
                 r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\5_Resample\LCZC_V1.3_resampled.tif",
                 100,gdal.GRA_Mode,gdal.GDT_UInt16,targetAlignedSign=False)