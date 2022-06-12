# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-24 11:30:20
# @Desc  : 将globeland30文件重采样并且进行重分类

import os.path
from osgeo import gdal, gdalconst
import numpy as np

origin_tiff_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\4.Mosaic\globeland30_2020.tif"
crop_tiff_folder=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\cropped"
rsrc_tiff_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\resampled&reclassified_4km"
'''
# 切割tiff文件
for N_lat in range(60,20,-10):
    for W_lon in range(70,140,10):
        print("lat:{},lon:{}".format(N_lat,W_lon))
        print(os.path.join(crop_tiff_folder,os.path.splitext(origin_tiff_file.split("\\")[-1])[0]+"_lat{}lon{}".format(N_lat,W_lon)+".tif"))
        gdal.Warp(os.path.join(crop_tiff_folder,os.path.splitext(origin_tiff_file.split("\\")[-1])[0]+"_lat{}lon{}".format(N_lat,W_lon)+".tif"),
                  origin_tiff_file, format='GTiff', xRes=0.0003, yRes=0.0003,
                  outputBounds=[W_lon, N_lat-10, W_lon+10, N_lat],  # 西经，南纬，东经，北纬
                  outputType=gdal.GDT_Byte, resampleAlg=gdal.GRA_NearestNeighbour, targetAlignedPixels=True,
                  srcSRS='EPSG:4326', dstSRS='EPSG:4326')
'''
allfile=[]
for eachfile in os.listdir(crop_tiff_folder):
    allfile.append(eachfile)
for cropped_origin_tiff_file in allfile:
    # 重采样
    origin_tiff: gdal.Dataset=gdal.Open(os.path.join(crop_tiff_folder,cropped_origin_tiff_file),gdalconst.GA_ReadOnly)
    origin_geo=origin_tiff.GetGeoTransform()
    print([round(origin_geo[0]), round(origin_geo[3] - 10), round(origin_geo[0] + 10), round(origin_geo[3])])
    gdal.Warp(os.path.join(rsrc_tiff_file,"resampled_"+cropped_origin_tiff_file),origin_tiff, format='GTiff',xRes=0.04,yRes=0.04,
              outputBounds=[round(origin_geo[0]), round(origin_geo[3] - 10), round(origin_geo[0] + 10), round(origin_geo[3])], # 西经，南纬，东经，北纬
              outputType=gdal.GDT_Byte,resampleAlg=gdal.GRA_Mode,targetAlignedPixels=True,
              srcSRS='EPSG:4326', dstSRS='EPSG:4326')
    # 重分类
    resample_tiff: gdal.Dataset=gdal.Open(os.path.join(rsrc_tiff_file,"resampled_"+cropped_origin_tiff_file),gdalconst.GA_ReadOnly)
    resample_band: gdal.Band=resample_tiff.GetRasterBand(1)
    width,height=resample_tiff.RasterXSize,resample_tiff.RasterYSize
    value=resample_band.ReadAsArray()
    ref_value=value.copy()
    value[np.where(ref_value==10)]=12 # 耕地
    value[np.where(ref_value==20)]=5 # 林地
    value[np.where(ref_value==30)]=10 # 草地
    value[np.where(ref_value==40)]=7 # 灌木
    value[np.where(ref_value==50)]=11 # 湿地
    value[np.where(ref_value==60)]=17 # 江河湖泊
    value[np.where(ref_value==61)]=17 # 江河湖泊
    value[np.where(ref_value==62)]=17 # 江河湖泊
    value[np.where(ref_value==70)]=19 # 混合苔原
    value[np.where(ref_value==71)]=18 # 灌木苔原
    value[np.where(ref_value==72)]=18 # 禾本苔原
    value[np.where(ref_value==73)]=19 # 湿苔原
    value[np.where(ref_value==74)]=20 # 裸地苔原
    value[np.where(ref_value==80)]=13 # 人造地表
    value[np.where(ref_value==90)]=20 # 裸地
    value[np.where(ref_value==100)]=15 # 冰雪
    value[np.where(ref_value==255)]=17 # 水
    driver = gdal.GetDriverByName('GTiff')
    reclass_tiff: gdal.Dataset = driver.Create(os.path.join(rsrc_tiff_file,"reclassified_"+cropped_origin_tiff_file),
                                               xsize=width, ysize=height, bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
    reclass_band: gdal.Band = reclass_tiff.GetRasterBand(1)  # 类型注解
    reclass_band.WriteArray(value)
    reclass_band.SetNoDataValue(0)
    reclass_tiff.SetGeoTransform(resample_tiff.GetGeoTransform())  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    reclass_tiff.SetProjection(resample_tiff.GetProjection())  # SetProjection写入投影im_proj
    reclass_tiff.FlushCache()
    reclass_tiff.GetRasterBand(1).ComputeStatistics(True)
    reclass_tiff=None
'''
crop_tiff_folder=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\resampled&reclassified_100m"
rsrc_tiff_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\resampled&reclassified_500m"

# 切割tiff文件
for N_lat in range(60,20,-10):
    for W_lon in range(70,140,10):
        print("lat:{},lon:{}".format(N_lat,W_lon))
        print(os.path.join(crop_tiff_folder,"reclassified_globeland30_2020"+"_lat{}lon{}".format(N_lat,W_lon)+".tif"))
        gdal.Warp(os.path.join(rsrc_tiff_file,"reclassified_globeland30_2020"+"_lat{}lon{}".format(N_lat,W_lon)+".tif"),
                  os.path.join(crop_tiff_folder,"reclassified_globeland30_2020"+"_lat{}lon{}".format(N_lat,W_lon)+".tif"),
                  format='GTiff', xRes=0.004, yRes=0.004,
                  outputBounds=[W_lon, N_lat-10, W_lon+10, N_lat],  # 西经，南纬，东经，北纬
                  outputType=gdal.GDT_Byte, resampleAlg=gdal.GRA_Mode, targetAlignedPixels=True,
                  srcSRS='EPSG:4326', dstSRS='EPSG:4326')
'''

