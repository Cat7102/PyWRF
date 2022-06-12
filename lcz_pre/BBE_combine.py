# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-04-22 20:36:07
# @Desc  : 合成BBE信息，使用MYD21A2的29，31，32波段以及MOD09A1的7波段
#          使用的计算公式为：BBE=0.329 * b29 + 0.572 * b31 + 0.095
#          参考文献：
#          Li H, Liu Z, Mamtimin A, et al.
#          A new linear relation for estimating surface broadband emissivity in arid regions based on ftir and modis products[J].
#          Remote Sensing, 2021, 13(9): 1686.

from osgeo import gdal,gdalconst

def resample_bbe(inputfile):
    '''
    @param inputfile: 需要进行裁剪以及重采样的文件
    '''
    # TIFF影像裁剪
    tiff_data = gdal.Open(inputfile+".tif", gdalconst.GA_ReadOnly)
    print("裁剪"+inputfile+".tif")
    gdal.Warp(inputfile+"_resampled.tif", tiff_data, format='GTiff',
              xRes=0.001, yRes=0.001,
              outputBounds=[120.95, 30.691, 122.1, 31.873],
              outputType=gdal.GDT_Float32, resampleAlg=gdal.GRA_NearestNeighbour, targetAlignedPixels=False,
              srcSRS='EPSG:4326', dstSRS='EPSG:4326')

def cal_bbe(band7,band29,band31,band32,dstfile):
    '''
    @param band7: 波段7的文件
    @param band29: 波段29的文件
    @param band31: 波段31的文件
    @param band32: 波段32的文件
    @param dstfile: 保存路径
    '''
    tiff = gdal.Open(band7, gdalconst.GA_ReadOnly)
    tiff_width, tiff_height = tiff.RasterXSize, tiff.RasterYSize
    print(tiff_width, tiff_height)
    tiff_proj = tiff.GetProjection()  # 得到数据集的投影信息
    tiff_geo = tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
    b7 = tiff.GetRasterBand(1).ReadAsArray()
    b7=b7*0.0001
    tiff2 = gdal.Open(band29)
    b29 = tiff2.GetRasterBand(1).ReadAsArray()
    b29 = b29*0.002+0.49
    tiff3 = gdal.Open(band31)
    b31 = tiff3.GetRasterBand(1).ReadAsArray()
    b31 = b31*0.002+0.49
    tiff4 = gdal.Open(band32)
    b32 = tiff4.GetRasterBand(1).ReadAsArray()
    b32 = b32*0.002+0.49
    #bbe = 0.08 * b29 + 0.485 * b31 + 0.536 * b32 - 0.152 * b7  # bbe计算公式
    #bbe = 0.1828 * b29 + 0.3867 * b31 + 0.4395 * b32 # bbe计算公式
    bbe = 0.329 * b29 + 0.572 * b31 + 0.095 # bbe计算公式
    driver = gdal.GetDriverByName('GTiff')
    bbe_file = driver.Create(dstfile, xsize=tiff_width, ysize=tiff_height, bands=1,
                             eType=gdal.GDT_Float32, options=["TILED=YES", "COMPRESS=LZW"])
    bbe_file.GetRasterBand(1).WriteArray(bbe)
    bbe_file.SetGeoTransform(tiff_geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
    bbe_file.SetProjection(tiff_proj)  # SetProjection写入投影im_proj
    bbe_file.FlushCache()
    bbe_file.GetRasterBand(1).ComputeStatistics(True)  # 统计值
    bbe_file.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
    print(dstfile+"计算完成")

if __name__ == '__main__':
    pathlist=["MOD09A1_A2021025_h28v05_b7","MOD09A1_A2021257_h28v05_b7","MYD21A2_A2021025_h28v05_b29","MYD21A2_A2021025_h28v05_b31","MYD21A2_A2021025_h28v05_b32"
        ,"MYD21A2_A2021257_h28v05_b29","MYD21A2_A2021257_h28v05_b31","MYD21A2_A2021257_h28v05_b32"]
    for path in pathlist:
        resample_bbe(path)
    Jan_path=["MOD09A1_A2021025_h28v05_b7_resampled.tif","MYD21A2_A2021025_h28v05_b29_resampled.tif"
        ,"MYD21A2_A2021025_h28v05_b31_resampled.tif","MYD21A2_A2021025_h28v05_b32_resampled.tif"]
    Jun_path=["MOD09A1_A2021257_h28v05_b7_resampled.tif","MYD21A2_A2021257_h28v05_b29_resampled.tif"
        ,"MYD21A2_A2021257_h28v05_b31_resampled.tif","MYD21A2_A2021257_h28v05_b32_resampled.tif"]
    cal_bbe(Jan_path[0],Jan_path[1],Jan_path[2],Jan_path[3],"MODIS_BBE_Jan_sh.tif")
    cal_bbe(Jun_path[0],Jun_path[1],Jun_path[2],Jun_path[3],"MODIS_BBE_Jun_sh.tif")