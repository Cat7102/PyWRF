# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-19 18:43:43
# @Desc  : 将逐月的分图幅tiff文件进行mosaic

import os

import numpy as np
from osgeo import gdal, gdalconst, osr

#  specifies the path to the input data
inpath_root = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_3.Monthly'
#  specifies the path to the output data
outpath = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_4.MonthlyMosaic'
# os.chdir(inpath) # change the current working directory to the input data directory

for month in range(1,13,1):
    inpath=os.path.join(inpath_root,str(month).zfill(2))
    #  gets all the hdf files in the current folder
    allfiles = os.listdir(inpath)
    alltiffiles, indexlist = [], []
    for eachfile in allfiles:
        if os.path.splitext(eachfile)[1] == '.tif':
            alltiffiles.append(eachfile)
            indexlist.append(eachfile.split("_")[2] + "_" + eachfile.split("_")[3])
    indexlist = list(set(indexlist))
    indexlist.sort()
    print("{}文件夹中的编号以及波段序列为：\n{}".format(inpath, indexlist))

    ##################################################################################################################################################
    # Fpar处理片段
    value_array = []
    NorthLat, SouthLat, WestLon, EastLon = [], [], [], []
    Size = []
    X_Index, Y_Index = [], []
    # 将数值进行存储
    for index in indexlist:
        tiffile = os.path.join(inpath, "monthly_Fpar_" + index)
        print("读取数据：{}".format(tiffile))
        tiff = gdal.Open(tiffile, gdalconst.GA_ReadOnly)
        each_valuearray = tiff.GetRasterBand(1).ReadAsArray()
        each_geo = tiff.GetGeoTransform()
        value_array.append(each_valuearray)
        column, row = tiff.RasterXSize, tiff.RasterYSize  # 列与行
        each_NorthLat, each_WestLon = each_geo[3], each_geo[0]  # 北纬，西经
        each_SouthLat, each_EastLon = each_geo[3] + row * each_geo[5], each_geo[0] + column * each_geo[1]  # 南纬，东经
        if X_Index == []:
            X_Index.append(0)
            Y_Index.append(0)
        else:
            Y_Index.append(round((each_NorthLat - NorthLat[0]) / each_geo[-1]))
            X_Index.append(round((each_WestLon - WestLon[0]) / each_geo[1]))
        Size.append([row, column])
        NorthLat.append(each_NorthLat), WestLon.append(each_WestLon)
        SouthLat.append(each_SouthLat), EastLon.append(each_EastLon)
    # 由于第一个文件的经纬度并不一定是最左端以及最右端，因此需要对X_Index与Y_Index进行偏移
    print(X_Index)
    print(Y_Index)
    print("X_Index与Y_Index的最小值分别为：{}，{}".format(min(X_Index), min(Y_Index)))
    X_Index, Y_Index = np.array(X_Index), np.array(Y_Index)
    X_Index = X_Index + abs(min(X_Index))
    Y_Index = Y_Index + abs(min(Y_Index))
    print("经过坐标偏移之后的坐标索引为：")
    print(X_Index)
    print(Y_Index)
    # 进行数据拼接
    print("创建空矩阵")
    mosaic_array = np.ones([np.max(Y_Index) + Size[np.argmax(Y_Index)][0], np.max(X_Index) + Size[np.argmax(X_Index)][1]])
    mosaic_array = mosaic_array * 255
    for i in range(len(value_array)):
        print("写入数据：{}".format(i))
        # 这里采用的原理是，先将数据对应的片段切割出来
        # 之后根据切割出的数据中有效数值（非255）的位置，将新数据的对应位置清零
        # 之后将切割出数据中的无效数值（255）清零
        # 然后两个矩阵相加，最后将切割矩阵替换原矩阵中的对应位置
        x_start, x_end = X_Index[i], X_Index[i] + Size[i][1]
        y_start, y_end = Y_Index[i], Y_Index[i] + Size[i][0]
        temp_slice = mosaic_array[y_start:y_end, x_start:x_end]
        value = value_array[i]
        value[np.where(temp_slice != 255)] = 0
        temp_slice[np.where(temp_slice == 255)] = 0
        print(np.shape(temp_slice), np.shape(value))
        temp_slice = temp_slice + value
        mosaic_array[y_start:y_end, x_start:x_end] = temp_slice

    # 创建投影信息
    outRasterSRS = osr.SpatialReference()
    # 代码4326表示WGS84坐标
    outRasterSRS.ImportFromEPSG(4326)
    # 创建地理信息
    local_geotrans = [0, 0.004166666666290, 0, 0, 0, -0.004166666666290]  # 每一张裁剪图的本地放射变化参数，0，3代表左上角坐标
    local_geotrans[0] = min(WestLon)  # 西经
    local_geotrans[3] = max(NorthLat)  # 北纬
    local_geotrans = tuple(local_geotrans)
    driver = gdal.GetDriverByName('GTiff')
    # 类型注解
    mosaic_tiff: gdal.Dataset = driver.Create(os.path.join(outpath, "2021_" + inpath.split("\\")[-1] + "_Fpar.tif"),
                                              xsize=int(np.max(X_Index) + Size[np.argmax(X_Index)][1]),
                                              ysize=int(np.max(Y_Index) + Size[np.argmax(Y_Index)][0]),
                                              bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
    mosaic_band: gdal.Band = mosaic_tiff.GetRasterBand(1)  # 类型注解
    mosaic_band.WriteArray(mosaic_array)
    mosaic_band.SetNoDataValue(255)
    mosaic_tiff.SetGeoTransform(local_geotrans)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    mosaic_tiff.SetProjection(outRasterSRS.ExportToWkt())  # SetProjection写入投影im_proj
    mosaic_tiff.FlushCache()
    mosaic_tiff.GetRasterBand(1).ComputeStatistics(True)

    ##################################################################################################################################################
    # LAI处理片段
    value_array = []
    NorthLat, SouthLat, WestLon, EastLon = [], [], [], []
    Size = []
    X_Index, Y_Index = [], []
    # 将数值进行存储
    for index in indexlist:
        tiffile = os.path.join(inpath, "monthly_Lai_" + index)
        print("读取数据：{}".format(tiffile))
        tiff = gdal.Open(tiffile, gdalconst.GA_ReadOnly)
        each_valuearray = tiff.GetRasterBand(1).ReadAsArray()
        each_geo = tiff.GetGeoTransform()
        value_array.append(each_valuearray)
        column, row = tiff.RasterXSize, tiff.RasterYSize  # 列与行
        each_NorthLat, each_WestLon = each_geo[3], each_geo[0]  # 北纬，西经
        each_SouthLat, each_EastLon = each_geo[3] + row * each_geo[5], each_geo[0] + column * each_geo[1]  # 南纬，东经
        if X_Index == []:
            X_Index.append(0)
            Y_Index.append(0)
        else:
            Y_Index.append(round((each_NorthLat - NorthLat[0]) / each_geo[-1]))
            X_Index.append(round((each_WestLon - WestLon[0]) / each_geo[1]))
        Size.append([row, column])
        NorthLat.append(each_NorthLat), WestLon.append(each_WestLon)
        SouthLat.append(each_SouthLat), EastLon.append(each_EastLon)
    # 由于第一个文件的经纬度并不一定是最左端以及最右端，因此需要对X_Index与Y_Index进行偏移
    print(X_Index)
    print(Y_Index)
    print("X_Index与Y_Index的最小值分别为：{}，{}".format(min(X_Index), min(Y_Index)))
    X_Index, Y_Index = np.array(X_Index), np.array(Y_Index)
    X_Index = X_Index + abs(min(X_Index))
    Y_Index = Y_Index + abs(min(Y_Index))
    print("经过坐标偏移之后的坐标索引为：")
    print(X_Index)
    print(Y_Index)
    # 进行数据拼接
    print("创建空矩阵")
    mosaic_array = np.ones([np.max(Y_Index) + Size[np.argmax(Y_Index)][0], np.max(X_Index) + Size[np.argmax(X_Index)][1]])
    mosaic_array = mosaic_array * 255
    for i in range(len(value_array)):
        print("写入数据：{}".format(i))
        x_start, x_end = X_Index[i], X_Index[i] + Size[i][1]
        y_start, y_end = Y_Index[i], Y_Index[i] + Size[i][0]
        temp_slice = mosaic_array[y_start:y_end, x_start:x_end]
        value = value_array[i]
        value[np.where(temp_slice != 255)] = 0
        temp_slice[np.where(temp_slice == 255)] = 0
        print(np.shape(temp_slice), np.shape(value))
        temp_slice = temp_slice + value
        mosaic_array[y_start:y_end, x_start:x_end] = temp_slice

    # 创建投影信息
    outRasterSRS = osr.SpatialReference()
    # 代码4326表示WGS84坐标
    outRasterSRS.ImportFromEPSG(4326)
    # 创建地理信息
    local_geotrans = [0, 0.004166666666290, 0, 0, 0, -0.004166666666290]  # 每一张裁剪图的本地放射变化参数，0，3代表左上角坐标
    local_geotrans[0] = min(WestLon)  # 西经
    local_geotrans[3] = max(NorthLat)  # 北纬
    local_geotrans = tuple(local_geotrans)
    driver = gdal.GetDriverByName('GTiff')
    # 类型注解
    mosaic_tiff: gdal.Dataset = driver.Create(os.path.join(outpath, "2021_" + inpath.split("\\")[-1] + "_Lai.tif"),
                                              xsize=int(np.max(X_Index) + Size[np.argmax(X_Index)][1]),
                                              ysize=int(np.max(Y_Index) + Size[np.argmax(Y_Index)][0]),
                                              bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
    mosaic_band: gdal.Band = mosaic_tiff.GetRasterBand(1)  # 类型注解
    mosaic_band.WriteArray(mosaic_array)
    mosaic_band.SetNoDataValue(255)
    mosaic_tiff.SetGeoTransform(local_geotrans)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    mosaic_tiff.SetProjection(outRasterSRS.ExportToWkt())  # SetProjection写入投影im_proj
    mosaic_tiff.FlushCache()
    mosaic_tiff.GetRasterBand(1).ComputeStatistics(True)
