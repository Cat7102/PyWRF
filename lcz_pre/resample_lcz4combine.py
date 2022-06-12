# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-03-26 01:28:26
# @Desc  : 将tiff文件重采样，可以提升或降低分辨率,专用于lcz
import numpy as np
from osgeo import gdal,gdalconst
import os,time

def search_most_class(array,x,y):
    '''
    搜索检索点范围内出现次数组多的城市分类
    @param array: 数据
    @param x: 检索点列
    @param y: 检索点行
    @return: most_class
    '''
    r=10
    while True:
        range_data=array[y-r:y+r,x-r:x+r]
        range_data=range_data[np.where(range_data>30)] # 只保留大于30的部分
        if range_data.size!=0:
            most_class = np.argmax(np.bincount(range_data.flatten()))  # 首先需要将数组转化为1维，之后找出现次数最多的分类（使用了bincount()与argmax()）
            print("{}范围内出现次数最多的分类为：{}".format(2*r+1,most_class))
            break
        else:
            print("没有找到城市分类，将扩大范围至r={}".format(r+2))
            r+=2
    return most_class

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
    tiff_new.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
    del tiff_new
    print("优化完成，耗时为：{}s".format(time.time() - start))

def resample_tsing2017(inputfile,outputfile,resolution,method,type,bound1=120.95,bound2=30.6,bound3=122.1,bound4=31.9,targetAlignedSign=True):
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
    retiff_list_origin = retiff_band.ReadAsArray()
    # 重分类
    retiff_list = retiff_list_origin.copy()  # 此前这里没有添加copy方法，导致出现了一个很严重的错误，即位于后部分的代码会将之前修改好的数值继续修改
    retiff_list[np.where(retiff_list_origin == 1)] = 12 # 农田
    retiff_list[np.where(retiff_list_origin == 8)] = 13 # 人造地表
    retiff_list[np.where(retiff_list_origin == 9)] = 16 # 裸地
    retiff_list[np.where(retiff_list_origin == 2)] = 5 # 林地
    retiff_list[np.where(retiff_list_origin == 3)] = 10 # 草地
    retiff_list[np.where(retiff_list_origin == 4)] = 7 # 灌木
    retiff_list[np.where(retiff_list_origin == 5)] = 11 # 湿地
    retiff_list[np.where(retiff_list_origin == 6)] = 17 # 水体
    retiff_list[np.where(retiff_list_origin == 7)] = 19 # 荒地
    retiff_list[np.where(retiff_list_origin == 10)] = 15 # 冰雪
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

def combine_lcz_tsing2017(originclass_tiff,lcz_tiff,dst_tiff):
    '''
    这是修改版的lcz文件与原有分类结合。
    加入新功能：对未进行分类的城市地表进行检索，并将最近范围内最多的城市地表类型赋予其值
    @param originclass_tiff: 原有的分类文件
    @param lcz_tiff: 训练后的lcz文件
    @param dst_tiff: 保存文件
    @return: None
    '''
    print(lcz_tiff+"开始修改")
    # 获取lczmap的数据
    lcz_tiff_data = gdal.Open(lcz_tiff,gdalconst.GA_ReadOnly)
    lcz_width,lcz_height=lcz_tiff_data.RasterXSize,lcz_tiff_data.RasterYSize
    lcz_tiff_band = lcz_tiff_data.GetRasterBand(1)
    lcz_list_array = lcz_tiff_band.ReadAsArray()
    # 获取基础landuse数据
    originclass_tiff_data = gdal.Open(originclass_tiff,gdalconst.GA_ReadOnly)
    originclass_tiff_width, originclass_tiff_height = originclass_tiff_data.RasterXSize, originclass_tiff_data.RasterYSize
    originclass_tiff_proj = originclass_tiff_data.GetProjection()  # 得到数据集的投影信息
    originclass_tiff_geo = originclass_tiff_data.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
    originclass_tiff_band = originclass_tiff_data.GetRasterBand(1)
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
    edt_list_array[np.where(lcz_list_array == 104)] = 12
    edt_list_array[np.where(lcz_list_array == 105)] = 41
    # 将lcz范围内没有触及到的13分类重新进行分类
    count_13=0
    for i in range(lcz_height):        #i表示纬度索引
        for j in range(lcz_width):    #j表示经度索引
            if edt_list_array[i,j]==13:
                print(i,j)
                edt_list_array[i,j]=search_most_class(edt_list_array,i,j)
                count_13+=1
    print("共有{}个13分类点没有进行分类,占比为{}%".format(count_13,count_13/(lcz_height*lcz_width)*100))
    driver = gdal.GetDriverByName('GTiff')
    file2 = driver.Create(dst_tiff, xsize=originclass_tiff_width, ysize=originclass_tiff_height, bands=1,
                          eType=gdal.GDT_UInt16, options=["TILED=YES", "COMPRESS=LZW"])
    file2.GetRasterBand(1).WriteArray(edt_list_array)
    file2.SetGeoTransform(originclass_tiff_geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    file2.SetProjection(originclass_tiff_proj)  # SetProjection写入投影im_proj
    print("修改完成")

if __name__ == '__main__':
    resample_lcz(r"..\6_Reprojection\LCZC_v1.3_100m_wgs84.tif",r"LCZC_wgs84_resampled.tif",
                 0.001,gdal.GRA_Mode,gdal.GDT_UInt16,targetAlignedSign=True)
    resample_tsing2017(r"Tsinghua2017_120E40N3.tif",r"Tsinghua2017_resampled.tif",
                       0.001,gdal.GRA_Mode,gdal.GDT_UInt16,targetAlignedSign=True)
    combine_lcz_tsing2017("Tsinghua2017_resampled.tif","LCZC_wgs84_resampled.tif","LCZC_Tsing2017_100m_wgs84.tif")