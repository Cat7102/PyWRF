# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-24 19:59:12
# @Desc  : 将globeland30与训练后的lcz分类相结合

import os.path
from osgeo import gdal, gdalconst
import numpy as np

def search_most_class(array,x,y,max_x,max_y):
    '''
    搜索检索点范围内出现次数组多的城市分类
    @param array: 数据
    @param x: 检索点列
    @param y: 检索点行
    @return: most_class
    '''
    r=10
    while True:
        if y-r<0:
            top=0
        else:
            top=y-r
        if y+r>max_y:
            bottom=max_y
        else:
            bottom=y+r
        if x-r<0:
            left=0
        else:
            left=x-r
        if x+r>max_x:
            right=max_x
        else:
            right=x+r
        range_data=array[top:bottom,left:right]
        print([top,bottom,left,right])
        #range_data=range_data[np.where(range_data>30)] # 只保留大于30的部分
        if range_data.size!=0:
            most_class = np.argmax(np.bincount(range_data.flatten()))  # 首先需要将数组转化为1维，之后找出现次数最多的分类（使用了bincount()与argmax()）
            print("{}范围内出现次数最多的分类为：{}".format(2*r+1,most_class))
            break
        else:
            print("没有找到城市分类，将扩大范围至r={}".format(r+2))
            r+=2
    return most_class

globeland30_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\resampled&reclassified_100m\reclassified_globeland30_2020_lat40lon120.tif"
resampled_globeland30_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\sh_globeland30_100m.tif"

gdal.Warp(resampled_globeland30_file,globeland30_file,format='GTiff', xRes=0.001, yRes=0.001,
          outputBounds=[120.95,30.6,122.1,31.9],  # 西经，南纬，东经，北纬
          outputType=gdal.GDT_Byte, resampleAlg=gdal.GRA_NearestNeighbour, targetAlignedPixels=True,
          srcSRS='EPSG:4326', dstSRS='EPSG:4326')

lcz_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\7_CombineTsinghua2017\LCZC_wgs84_resampled.tif"
globeland30_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\7_CombineTsinghua2017\sh_globeland30_100m.tif"
dst_file=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\7_CombineTsinghua2017\LCZC_globeland30_100m_wgs84.tif"

print("开始结合lcz数据")
# 获取lczmap的数据
lcz_tiff_data: gdal.Dataset=gdal.Open(lcz_file,gdalconst.GA_ReadOnly)
lcz_tiff_band: gdal.Band=lcz_tiff_data.GetRasterBand(1)
lcz_width,lcz_height=lcz_tiff_data.RasterXSize,lcz_tiff_data.RasterYSize
lcz_list_array = lcz_tiff_band.ReadAsArray()
# 获取基础landuse数据
originclass_tiff_data: gdal.Dataset=gdal.Open(globeland30_file,gdalconst.GA_ReadOnly)
originclass_tiff_band: gdal.Band=originclass_tiff_data.GetRasterBand(1)
originclass_tiff_width, originclass_tiff_height = originclass_tiff_data.RasterXSize, originclass_tiff_data.RasterYSize
originclass_tiff_proj = originclass_tiff_data.GetProjection()  # 得到数据集的投影信息
originclass_tiff_geo = originclass_tiff_data.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
edt_list_array = originclass_tiff_band.ReadAsArray()
# 将lcz写入基础landuse数据
edt_list_array[np.where(lcz_list_array == 1)] = 31
edt_list_array[np.where(lcz_list_array == 2)] = 32
edt_list_array[np.where(lcz_list_array == 3)] = 33
edt_list_array[np.where(lcz_list_array == 4)] = 34
edt_list_array[np.where(lcz_list_array == 5)] = 35
edt_list_array[np.where(lcz_list_array == 6)] = 36
edt_list_array[np.where(lcz_list_array == 7)] = 37
edt_list_array[np.where(lcz_list_array == 8)] = 38
edt_list_array[np.where(lcz_list_array == 9)] = 39
edt_list_array[np.where(lcz_list_array == 10)] = 40
edt_list_array[np.where(lcz_list_array == 101)] = 5
edt_list_array[np.where(lcz_list_array == 102)] = 5
edt_list_array[np.where(lcz_list_array == 103)] = 6
edt_list_array[np.where(lcz_list_array == 105)] = 41
# 将lcz范围内没有触及到的13分类重新进行分类
count_13=0
for i in range(lcz_height):        #i表示纬度索引
    for j in range(lcz_width):    #j表示经度索引
        if edt_list_array[i,j]==13:
            print(i,j)
            edt_list_array[i,j]=search_most_class(edt_list_array,j,i,originclass_tiff_width,originclass_tiff_height)
            count_13+=1
print("共有{}个13分类点没有进行分类,占比为{}%".format(count_13,count_13/(lcz_height*lcz_width)*100))
driver = gdal.GetDriverByName('GTiff')
dst_tiff: gdal.Dataset=driver.Create(dst_file, xsize=originclass_tiff_width, ysize=originclass_tiff_height, bands=1,
                                     eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
dst_band: gdal.Band=dst_tiff.GetRasterBand(1)
dst_band.WriteArray(edt_list_array)
dst_band.SetNoDataValue(0)
dst_tiff.SetGeoTransform(originclass_tiff_geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
dst_tiff.SetProjection(originclass_tiff_proj)  # SetProjection写入投影im_proj
dst_tiff.FlushCache()
dst_band.ComputeStatistics(True)
print("修改完成")