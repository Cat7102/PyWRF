# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-04-24 20:22:20
# @Desc  : 根据landsat8计算NDVI值

from osgeo import gdal,gdalconst
import numpy as np
import time

def ndvi_ls8_cal(landsat8_path,ndvi_path,ndwiflags_path):
    '''
    水体分割参考文献：[1]王大钊,王思梦,黄昌.Sentinel-2和Landsat8影像的四种常用水体指数地表水体提取对比[J].国土资源遥感,2019,31(03):157-165.
    @param landsat8_path: landsat8文件路径
    @param dst_path: 保存路径
    @return: None
    '''
    ls8_tiff=gdal.Open(landsat8_path,gdalconst.GA_ReadOnly)
    width,height=ls8_tiff.RasterXSize,ls8_tiff.RasterYSize
    proj = ls8_tiff.GetProjection()  # 得到数据集的投影信息
    geo = ls8_tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
    nir_band=ls8_tiff.GetRasterBand(5)
    r_band=ls8_tiff.GetRasterBand(4)
    g_band=ls8_tiff.GetRasterBand(3)
    nir_data=nir_band.ReadAsArray()
    r_data=r_band.ReadAsArray()
    g_data=g_band.ReadAsArray()
    nir_r=nir_data+r_data
    nir_g=g_data+nir_data
    nir_r[np.where(nir_r==0)]=1
    nir_g[np.where(nir_g==0)]=1
    ndvi=(nir_data-r_data)/nir_r
    ndwi=(g_data-nir_data)/nir_g
    ndwi_flag=np.zeros_like(ndwi)
    # 取1%~99%的置信区间
    ndvi[np.where(ndvi<=np.percentile(ndvi,2))]=np.percentile(ndvi,2)
    ndvi[np.where(ndvi>=np.percentile(ndvi,98))]=np.percentile(ndvi,98)
    # 水体分割阈值
    ndwi_flag[np.where(ndwi<=-0.15)]=0 # 陆地
    ndwi_flag[np.where(ndwi>-0.15)]=1 # 水体
    # 保存文件
    driver = gdal.GetDriverByName('GTiff')
    ndvi_file = driver.Create(ndvi_path, xsize=width,ysize=height, bands=2,
                                eType=gdal.GDT_Float32, options=["TILED=YES", "COMPRESS=LZW"])
    ndvi_file.GetRasterBand(1).WriteArray(ndvi)
    ndvi_file.GetRasterBand(2).WriteArray(ndwi)
    ndvi_file.SetGeoTransform(geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    ndvi_file.SetProjection(proj)  # SetProjection写入投影im_proj
    ndvi_file.FlushCache()
    ndvi_file.GetRasterBand(1).ComputeStatistics(True)
    ndvi_file.GetRasterBand(2).ComputeStatistics(True)
    # 保存ndwi
    driver = gdal.GetDriverByName('GTiff')
    ndwiflags_file = driver.Create(ndwiflags_path, xsize=width,ysize=height, bands=1,eType=gdal.GDT_Int16, options=["TILED=YES", "COMPRESS=LZW"])
    ndwiflags_file.GetRasterBand(1).WriteArray(ndwi_flag)
    ndwiflags_file.SetGeoTransform(geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    ndwiflags_file.SetProjection(proj)  # SetProjection写入投影im_proj
    ndwiflags_file.FlushCache()

def resample_lcz(inputfile,outputfile,resolution,method,type,bound1=120.95,bound2=30.6,bound3=122.1,bound4=31.9,targetAlignedSign=True):
    start=time.time()
    tiff_data = gdal.Open(inputfile, gdalconst.GA_ReadOnly)
    print("开始转换：" + inputfile)
    gdal.Warp(outputfile, tiff_data, format='GTiff',
              xRes=resolution, yRes=resolution,
              outputBounds=[bound1,bound2,bound3,bound4],
              outputType=type, resampleAlg=method, targetAlignedPixels=targetAlignedSign,
              srcSRS='EPSG:4326', dstSRS='EPSG:4326')
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
    #tiff_new.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
    del tiff_new
    print("优化完成，耗时为：{}s".format(time.time() - start))

if __name__=="__main__":
    ndvi_path = "2021_ndvi_sh.tif"
    ndwiflags_path = "2021_ndwiflags_sh.tif"
    landsat8_path = "flaash_2021_sh_wgs84.tif"
    ndvi_ls8_cal(landsat8_path,ndvi_path,ndwiflags_path)
    resample_lcz("2021_ndvi_sh.tif","2021_ndvi_sh_resampled.tif", 0.001,gdal.GRA_Bilinear,gdal.GDT_Float32,
                 bound1=120.95,bound2=30.691,bound3=122.1,bound4=31.873,targetAlignedSign=True)
    resample_lcz("2021_ndwiflags_sh.tif","2021_ndwiflag_sh_resampled.tif", 0.001,gdal.GRA_Mode,gdal.GDT_UInt16,targetAlignedSign=True)


