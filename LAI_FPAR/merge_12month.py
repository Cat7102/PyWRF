# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-21 20:15:27
# @Desc  : 将逐月的tiff合成到一个文件,并转为binary。目前已经弃用！
import time

from osgeo import gdal,gdalconst
import numpy as np
import os

def tiff2binary_file(tiff_file, bil_folder):
    options_list = ['-of ENVI']
    options_string = " ".join(options_list)
    print("开始转换binary:" + tiff_file)
    tiff_data = gdal.Open(tiff_file)
    # 栅格矩阵的列数
    tif_columns = tiff_data.RasterXSize
    # 栅格矩阵的行数
    tif_nrows = tiff_data.RasterYSize
    gdal.Translate(os.path.join(bil_folder,"00001" + "-" + str(tif_columns).zfill(5) + "." + "00001" + "-" + str(tif_nrows).zfill(5)) , tiff_file,
                   options=options_string)
    print(os.path.join(bil_folder,"00001" + "-" + str(tif_columns).zfill(5) + "." + "00001" + "-" + str(tif_nrows).zfill(5))  + "文件编译完成")

#  specifies the path to the input data
inpath = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_MonthlyMosaic'
#  specifies the path to the output data
outpath = r'D:\Data\WRF-Chem_Files\LAI_FPAR'

for band in ["Fpar","Lai"]:
    value_array=[]
    for i in range(1,13,1):
        eachtiff=os.path.join(inpath,"2021_"+str(i).zfill(2)+"_"+band+".tif")
        print(eachtiff)
        tiff = gdal.Open(eachtiff, gdalconst.GA_ReadOnly)
        data=tiff.GetRasterBand(1).ReadAsArray()
        value_array.append(data)
    driver = gdal.GetDriverByName('GTiff')
    year_tiff = driver.Create(os.path.join(outpath, "2021_" +band+".tif"),
                                xsize=tiff.RasterXSize, ysize=tiff.RasterYSize,
                                bands=12, eType=gdal.GDT_Float32, options=["TILED=YES", "COMPRESS=LZW","BIGTIFF=Yes"])
    year_tiff.SetGeoTransform(tiff.GetGeoTransform())  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    year_tiff.SetProjection(tiff.GetProjection())  # SetProjection写入投影im_proj
    # 分波段写入数据
    for i in range(1,13,1):
        print("开始写入月份：{}".format(i))
        year_tiff.GetRasterBand(i).WriteArray(value_array[i-1])
    year_tiff.FlushCache() # 需要先关闭tiff
    # 分波段计算其统计值
    for i in range (1,13,1):
        print("开始计算统计值：{}".format(i))
        year_tiff.GetRasterBand(i).ComputeStatistics(True)

time.sleep(2)
tiff2binary_file(r"D:\Data\WRF-Chem_Files\LAI_FPAR\2021_Fpar.tif",r"D:\Data\WRF-Chem_Files\LAI_FPAR\2021_Fpar")
tiff2binary_file(r"D:\Data\WRF-Chem_Files\LAI_FPAR\2021_Lai.tif",r"D:\Data\WRF-Chem_Files\LAI_FPAR\2021_Lai")