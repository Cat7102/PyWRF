# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-20 22:33:52
# @Desc  : 专用于modis文件的切割、重采样与转binary

from osgeo import gdal,gdalconst
import os,time

def progress(percent, msg, tag):
    """进度回调函数"""
    print(percent, msg, tag)

def tiff2binary(tiff,start_x=1,start_y=1, outfolder="./"):
    options_list = ['-of ENVI']
    options_string = " ".join(options_list)
    print("开始转换" + tiff)
    tiff_data = gdal.Open(tiff)
    # 栅格矩阵的列数
    tif_columns = tiff_data.RasterXSize
    # 栅格矩阵的行数
    tif_nrows = tiff_data.RasterYSize
    gdal.Translate(os.path.join(outfolder,str(start_x).zfill(5) + "-" + str(tif_columns+start_x-1).zfill(5) + "." + str(start_y).zfill(5) + "-"
                   + str(tif_nrows+start_y-1).zfill(5)), tiff, options=options_string)
    print(str(start_x).zfill(5) + "-" + str(tif_columns+start_x-1).zfill(5) + "." + str(start_y).zfill(5) + "-"
                   + str(tif_nrows+start_y-1).zfill(5) + "文件编译完成")

def mergeband(inputname_list,outputname):
    '''
    @param inputname_list: 多波段的文件
    @param outputname: 输出文件的名字
    '''
    print("开始合成多波段：{}".format(outputname))
    value_array = []
    for tiff in inputname_list:
        tiff_data = gdal.Open(tiff, gdalconst.GA_ReadOnly)
        data = tiff_data.GetRasterBand(1).ReadAsArray()
        value_array.append(data)
    driver = gdal.GetDriverByName('GTiff')
    merge_tiff: gdal.Dataset=driver.Create(outputname, xsize=tiff_data.RasterXSize, ysize=tiff_data.RasterYSize, bands=12, eType=gdal.GDT_UInt16) # 类型注解语法
    merge_tiff.SetGeoTransform(tiff_data.GetGeoTransform())  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    merge_tiff.SetProjection(tiff_data.GetProjection())  # SetProjection写入投影im_proj
    tiff_data = None  # 关闭读取的分波段文件，需要在读取完了需要的数据以后再关闭
    # 分波段写入数据
    for i in range(1,13,1):
        print("{}写入月份：{}".format(outputname,i))
        merge_band: gdal.Band=merge_tiff.GetRasterBand(i) # 类型注解语法
        merge_band.WriteArray(value_array[i-1])
        merge_band.SetNoDataValue(255)
    merge_tiff.FlushCache() # 需要关闭tiff
    print("移除缓存文件")
    for tiff in inputname_list:
        os.remove(tiff)

def crop_tiff(inputtiff_folder,year, outtiff_base, resolution, ul_lon, ul_lat, tile_xsize, tile_ysize, tile_x, tile_y, method=gdal.GRA_NearestNeighbour, align=True):
    """
    输出文件夹下所有文件名
    :param inputtiff_folder: 12个月分月份tiff文件的文件夹
    :param year: 数据的年份
    :param outtiff_base: 输出文件的基础命名
    :param resolution: 分辨率
    :param ul_lon: 最左上角的经度
    :param ul_lat: 最左上角的纬度
    :param tile_xsize: 单个tile的x方向单位
    :param tile_ysize: 单个tile的y方向单位
    :param tile_x: x方向tile个数
    :param tile_y: y方向tile个数
    :param method: 重采样方法
    :param align: 是否网格对齐
    :return:
    """
    #tiff_data.RasterCount # 获取tiffdata的总波段数
    os.makedirs("cropped")
    os.makedirs("cropped_binary")
    # 由于gdal.wrap方法只支持单个波段，因此需要先进行分波段，再合成波段。
    for x in range(tile_x):
        for y in range(tile_y):
            print("开始转换:x={}, y={}".format(x,y))
            temptiff_list=[]
            for i in range(1,13,1):
                print("开始转换波段：{}".format(i))
                tiff_data=gdal.Open(os.path.join(inputtiff_folder,str(year)+"_"+str(i).zfill(2)+"_Fpar.tif"),gdalconst.GA_ReadOnly)
                gdal.Warp(outtiff_base+"_x"+str(x)+"_y"+str(y)+"_m"+str(i)+".tif", tiff_data, format='GTiff',
                          xRes=resolution, yRes=resolution,srcNodata=255,dstNodata=255,multithread=True,
                          outputBounds=[ul_lon+x*tile_xsize*resolution, ul_lat-(y+1)*resolution*tile_ysize,
                                        ul_lon+resolution*tile_xsize*(x+1), ul_lat-y*resolution*tile_ysize],
                          # 西经，南纬，东经，北纬
                          outputType=gdal.GDT_UInt16, resampleAlg=method, targetAlignedPixels=align,
                          srcSRS='EPSG:4326', dstSRS='EPSG:4326')
                temptiff_list.append(outtiff_base+"_x"+str(x)+"_y"+str(y)+"_m"+str(i)+".tif")
            mergeband(temptiff_list,os.path.join("cropped",outtiff_base+"_x"+str(x)+"_y"+str(y)+".tif"))
            print("开始转为binary文件")
            tiff2binary(os.path.join("cropped",outtiff_base+"_x"+str(x)+"_y"+str(y)+".tif"),start_x=x*tile_xsize+1,start_y=y*tile_ysize+1,outfolder="cropped_binary")
            info: gdal.Dataset=gdal.Open(os.path.join("cropped",outtiff_base+"_x"+str(x)+"_y"+str(y)+".tif"), gdalconst.GA_ReadOnly) # 类型注解语法
            geo = info.GetGeoTransform()
            print(geo)

def resample_tiff(inputtiff, outtiff, resolution, ul_lon, ul_lat, xsize, ysize, method=gdal.GRA_Mode, align=True):
    start=time.time()
    tiff_data = gdal.Open(inputtiff, gdalconst.GA_ReadOnly)
    print("开始转换：" + inputtiff)
    gdal.Warp(outtiff, tiff_data, format='GTiff',
              xRes=resolution, yRes=resolution,
              outputBounds=[ul_lon,ul_lat-resolution*ysize,ul_lon+resolution*(xsize-1),ul_lat], # 西经，南纬，东经，北纬
              outputType=gdal.GDT_UInt16, resampleAlg=method, targetAlignedPixels=align,
              srcSRS='EPSG:4326', dstSRS='EPSG:4326')
    print("转换完成，耗时为：{}s".format(time.time()-start))
    print("开始转换二进制")
    tiff2binary(outtiff)
    info = gdal.Open(outtiff, gdalconst.GA_ReadOnly)
    print(gdal.Info(info))

if __name__ == '__main__':
    #resample_tiff("MCD12Q1_2020_China.tif","MCD12Q1_2020_China_5km.tif",0.04,52.5,60,3000,1200)
    crop_tiff("../2021_4.MonthlyMosaic",2021,"2021_Fpar",0.004,81,50,3000,1200,10,10,method=gdal.GRA_Bilinear,align=False)
