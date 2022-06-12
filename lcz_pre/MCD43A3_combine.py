# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-04-22 20:36:07
# @Desc  : 合成MCD43A3图像

from osgeo import gdal,gdalconst

# BSA波段合成
bsa_pathlist=["MCD43A3_A2021082_h28v05_BSA.tif","MCD43A3_A2021113_h28v05_BSA.tif","MCD43A3_A2021133_h28v05_BSA.tif"]

tiff=gdal.Open(bsa_pathlist[0],gdalconst.GA_ReadOnly)
tiff_width, tiff_height = tiff.RasterXSize, tiff.RasterYSize
tiff_proj = tiff.GetProjection()  # 得到数据集的投影信息
tiff_geo = tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
data = tiff.GetRasterBand(1).ReadAsArray()
print(tiff_width,tiff_height)
tiff2=gdal.Open(bsa_pathlist[1])
data2 = tiff2.GetRasterBand(1).ReadAsArray()
tiff3=gdal.Open(bsa_pathlist[2])
data3 = tiff3.GetRasterBand(1).ReadAsArray()
new_data=data
for j in range(tiff_width):
    for i in range(tiff_height):
        count=0
        value=0
        if data[i,j]<30000:
            value=value+data[i,j]
            count+=1
        if data2[i,j]<30000:
            value=value+data2[i,j]
            count += 1
        if data3[i,j]<30000:
            value=value+data3[i,j]
            count += 1
        if count==0:
            new_data[i, j] = -1
        else:
            new_data[i,j]=value/count
    print(j/tiff_width)
driver = gdal.GetDriverByName('GTiff')
albedo_file = driver.Create(r"MCD43A3_BSA_shortwave.tif", xsize=tiff_width, ysize=tiff_height, bands=1,
                            eType=gdal.GDT_Int16, options=["TILED=YES", "COMPRESS=LZW"])
albedo_file.GetRasterBand(1).WriteArray(new_data)
albedo_file.SetGeoTransform(tiff_geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
albedo_file.SetProjection(tiff_proj)  # SetProjection写入投影im_proj
#albedo_file.FlushCache()
#albedo_file.GetRasterBand(1).ComputeStatistics(True)

# WSA波段合成
wsa_pathlist=["MCD43A3_A2021082_h28v05_WSA.tif","MCD43A3_A2021113_h28v05_WSA.tif","MCD43A3_A2021133_h28v05_WSA.tif"]

tiff=gdal.Open(wsa_pathlist[0],gdalconst.GA_ReadOnly)
tiff_width, tiff_height = tiff.RasterXSize, tiff.RasterYSize
tiff_proj = tiff.GetProjection()  # 得到数据集的投影信息
tiff_geo = tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
data = tiff.GetRasterBand(1).ReadAsArray()
print(tiff_width,tiff_height)
tiff2=gdal.Open(wsa_pathlist[1])
data2 = tiff2.GetRasterBand(1).ReadAsArray()
tiff3=gdal.Open(wsa_pathlist[2])
data3 = tiff3.GetRasterBand(1).ReadAsArray()
new_data=data
for j in range(tiff_width):
    for i in range(tiff_height):
        count=0
        value=0
        if data[i,j]<30000:
            value=value+data[i,j]
            count+=1
        if data2[i,j]<30000:
            value=value+data2[i,j]
            count += 1
        if data3[i,j]<30000:
            value=value+data3[i,j]
            count += 1
        if count==0:
            new_data[i, j] = -1
        else:
            new_data[i,j]=value/count
    print(j/tiff_width)
driver = gdal.GetDriverByName('GTiff')
albedo_file = driver.Create(r"MCD43A3_WSA_shortwave.tif", xsize=tiff_width, ysize=tiff_height, bands=1,
                            eType=gdal.GDT_Int16, options=["TILED=YES", "COMPRESS=LZW"])
albedo_file.GetRasterBand(1).WriteArray(new_data)
albedo_file.SetGeoTransform(tiff_geo)  # driver对象创建的dataset对象具有SetGeoTransform方法，写入仿射变换参数GEOTRANS
albedo_file.SetProjection(tiff_proj)  # SetProjection写入投影im_proj
#albedo_file.FlushCache()
#albedo_file.GetRasterBand(1).ComputeStatistics(True)

del albedo_file

# TIFF影像裁剪
tiff_data = gdal.Open("MCD43A3_WSA_shortwave.tif", gdalconst.GA_ReadOnly)
print("开始裁剪")
gdal.Warp("MCD43A3_WSA_shortwave_sh.tif", tiff_data, format='GTiff',
          xRes=0.001, yRes=0.001,
          outputBounds=[120.95,30.691,122.1,31.873],
          outputType=gdal.GDT_Int16, resampleAlg=gdal.GRA_NearestNeighbour, targetAlignedPixels=False,
          srcSRS='EPSG:4326', dstSRS='EPSG:4326')
tiff_data = gdal.Open("MCD43A3_BSA_shortwave.tif", gdalconst.GA_ReadOnly)
gdal.Warp("MCD43A3_BSA_shortwave_sh.tif", tiff_data, format='GTiff',
          xRes=0.001, yRes=0.001,
          outputBounds=[120.95,30.691,122.1,31.873],
          outputType=gdal.GDT_Int16, resampleAlg=gdal.GRA_NearestNeighbour, targetAlignedPixels=False,
          srcSRS='EPSG:4326', dstSRS='EPSG:4326')
print("开始优化")
del tiff_data
BSA_tiff = gdal.Open("MCD43A3_BSA_shortwave_sh.tif", gdalconst.GA_ReadOnly)
WSA_tiff = gdal.Open("MCD43A3_WSA_shortwave_sh.tif", gdalconst.GA_ReadOnly)
alb_width, alb_height = BSA_tiff.RasterXSize, BSA_tiff.RasterYSize
alb_proj = BSA_tiff.GetProjection()  # 得到数据集的投影信息
alb_geo = BSA_tiff.GetGeoTransform()  # 得到数据集的地理仿射信息,是一个包含六个元素的元组
bsa_band = BSA_tiff.GetRasterBand(1)
bsa_array = bsa_band.ReadAsArray()
wsa_band = WSA_tiff.GetRasterBand(1)
wsa_array = wsa_band.ReadAsArray()
driver = gdal.GetDriverByName('GTiff')
tiff_new = driver.Create("MCD43A3_Combine_shortwave_sh.tif", xsize=alb_width, ysize=alb_height,
                         bands=2, eType=gdal.GDT_Int16, options=["TILED=YES", "COMPRESS=LZW"])
tiff_new.SetProjection(alb_proj)  # SetProjection写入投影im_proj
tiff_new.SetGeoTransform(alb_geo)  # SetGeoTransform写入地理信息
tiff_new.GetRasterBand(1).WriteArray(bsa_array)
tiff_new.GetRasterBand(2).WriteArray(wsa_array)
tiff_new.FlushCache()
tiff_new.GetRasterBand(1).ComputeStatistics(True)  # 统计值
tiff_new.GetRasterBand(2).ComputeStatistics(True)  # 统计值
tiff_new.BuildOverviews('average', [2, 4, 8, 16, 32, 64, 128])  # 金字塔
del tiff_new
print("优化完成")