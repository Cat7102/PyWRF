# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-18 17:34:08
# @Desc  : 根据生成的tiff文件生成月平均波段

import os

import numpy as np
from osgeo import gdal, gdalconst

# specifies the path to the input data
inpath_root = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_2.GeoTiff'
# specifies the path to the output data
outpath_root = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_3.Monthly'
# os.chdir(inpath) # change the current working directory to the input data directory

for month in range(1,13,1):
    inpath=os.path.join(inpath_root,str(month).zfill(2))
    outpath = os.path.join(outpath_root, inpath.split("\\")[-1])

    if not os.path.exists(outpath):
        print("将创建文件夹：{}".format(outpath))
        os.makedirs(outpath)

    #  gets all the hdf files in the current folder
    allfiles = os.listdir(inpath)
    alltiffiles, filedatelist, indexlist = [], [], []
    for eachfile in allfiles:
        if os.path.splitext(eachfile)[1] == '.tif':
            alltiffiles.append(eachfile)
            filedatelist.append(eachfile.split("_")[0])  # 类似于：A2021121
            indexlist.append(eachfile.split("_")[1] + "_" + eachfile.split("_")[2])  # 类似于：h29v06_Fpar
    filedatelist = list(set(filedatelist))
    filedatelist.sort()
    indexlist = list(set(indexlist))
    indexlist.sort()
    # 删除质量控制的qc波段
    for i in indexlist:
        if i.split("_")[1] == "FparLai":
            indexlist.remove(i)
    print("{}文件夹中的时间序列为：\n{}".format(inpath, filedatelist))
    print("{}文件夹中的编号以及波段序列为：\n{}".format(inpath, indexlist))

    # 根据各个波段数据生成月平均数据
    for index in indexlist:
        print("开始计算卫星图幅：{}".format(index))
        value_array = 0  # 值矩阵，用于加和
        count_array = 0  # 计数矩阵，0表示值缺失，1表示值存在，最后用于计数计算平均值
        for date in filedatelist:
            print("加入数据：{}".format(date))
            eachfile = os.path.join(inpath, date + "_" + index + "_500m.tif")
            # 这里使用python的”类型注解“语法指定dataset的类型为gdal.Dataset，之后可实现自动补全
            tiff: gdal.Dataset = gdal.Open(eachfile, gdalconst.GA_ReadOnly)
            qc_tiff: gdal.Dataset = gdal.Open(os.path.join(inpath, date + "_" + index.split("_")[0] + "_FparLai_QC.tif"))
            # 生成临时矩阵，用于临时存储值
            temp_valuearray = tiff.GetRasterBand(1).ReadAsArray()
            copy_tempvalue = temp_valuearray.copy()
            temp_countarray = np.ones_like(temp_valuearray)
            qcarray = qc_tiff.GetRasterBand(1).ReadAsArray()
            '''
            由于卫星图的每个格点存在质量差异，因此需要筛选质量高的格点数据，以防质量差的数据造成错误
            根据MOD15 USER GUIDE，使用QC波段，并且只取值为000+00/01/10+0+0/1+0/1
            对应的十进制数为:
                [0,1,2,3,8,9,10,11,16,17,18,19]
            而24,25,26,27,32,33,34,35,40,41,42,43,48,49,50,51,56,57,58,59,64,65,66,67,72,73,74,75,80,81,82,83,88,89,90,91质量的值也可以
            但是对于上海地区来说要求较为严苛，因此不考虑。
            全部值为000/001+00/01/10+0+0/1+0/1
            '''
            valid_qc = [0, 1, 2, 3, 8, 9, 10, 11, 16, 17, 18, 19]
            temp_valuearray[np.where(np.isin(qcarray, valid_qc,
                                             invert=True))] = 0  # qcarray中的元素是否存在于valid_qc中，如果设置了invert=True,则qcarray中元素在valid_qc中返回False
            # 临时数据的处理过程，由于fpar以及lai的有效值范围为0~100，因此大于100全部认为0
            temp_valuearray[np.where(temp_valuearray >= 101)] = 0
            temp_countarray[np.where(temp_valuearray == 0)] = 0  # 无效值均处理为了0，计数也为0
            '''不再使用，因为使用整数型可以节省存储空间使用gdal.GDT_Byte
            if index.split("_")[1]=="Fpar":
                print("Scale Factor: 0.01")
                temp_valuearray=temp_valuearray*0.01
            else:
                print("Scale Factor: 0.1")
                temp_valuearray=temp_valuearray*0.1
            '''
            # 同一个图幅下的值进行不断累加
            value_array = value_array + temp_valuearray
            count_array = count_array + temp_countarray
        count_array[np.where(value_array == 0)] = 1  # 如果累加以后value等于0，表示所有图幅下全部缺失，则将count改为1方便矩阵的除法
        value_array = value_array / count_array
        value_array[np.where(copy_tempvalue == 255)] = 255  # 由于100~254均为实际0的值，而255则为填充值，因此需要返还值
        # 存储计算的数值
        print("保存文件并进行优化：{}".format(index))
        driver = gdal.GetDriverByName('GTiff')
        # 类型注解
        monthly_tiff: gdal.Dataset = \
            driver.Create(os.path.join(outpath, "monthly_" + index.split("_")[1] + "_" + inpath.split("\\")[-1] + "_" +index.split("_")[0] + ".tif"),
                          xsize=tiff.RasterXSize, ysize=tiff.RasterYSize, bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
        monthly_band: gdal.Band = monthly_tiff.GetRasterBand(1)  # 类型注解
        monthly_band.WriteArray(value_array)
        monthly_band.SetNoDataValue(255)
        monthly_tiff.SetGeoTransform(tiff.GetGeoTransform())  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
        monthly_tiff.SetProjection(tiff.GetProjection())  # SetProjection写入投影im_proj
        monthly_tiff.FlushCache()
        # monthly_tiff.GetRasterBand(1).ComputeStatistics(True)
