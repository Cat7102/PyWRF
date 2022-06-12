# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-23 23:51:13
# @Desc  : 将globeland30的分幅tiff均投影为WGS84类型，并且重采样至规整的resolution

from osgeo import gdal,osr,gdalconst
import os,osgeo

inpath=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\2.GeoTiff"
dstpath=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\3.Reprojection"

# 检索文件夹下所有的tiff
allfiles = os.listdir(inpath)
alltiff = []
gdal.SetConfigOption("OSR_USE_APPROX_TMERC","YES")
for eachfile in allfiles:
    if os.path.splitext(eachfile)[1] == '.tif':
        alltiff.append(eachfile)
# 方法一：采用gdal.Wrap方法进行重投影，之后采用重新构建tiff的方式优化tiff。（推荐，效率更高）
for tiff in alltiff:
    print(tiff+"开始重投影")
    src_data: gdal.Dataset=gdal.Open(os.path.join(inpath,tiff),gdalconst.GA_ReadOnly)
    print(src_data.GetGeoTransform())
    # 获取源数据坐标信息并转换格式
    srcSRS_wkt = src_data.GetProjection()
    srcSRS = osr.SpatialReference()
    # 这是一个在gdal3.0以上版本才会出现的问题
    # 如果不加下面的代码，使用osr.CoordinateTransformation.TransformPoint()的时候会出现这样的状况：
    # longitude,latitude,z=osr.CoordinateTransformation.TransformPoint(latitude,longitude)
    # 换言之就是返回的经纬度与输入的经纬度相反
    if int(osgeo.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        srcSRS.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    srcSRS.ImportFromWkt(src_data.GetProjection())
    # 获取源数据栅格尺寸
    src_width = src_data.RasterXSize
    src_height = src_data.RasterYSize
    src_bandcount = src_data.RasterCount
    # 获取源图像的仿射变换参数
    src_trans = src_data.GetGeoTransform()
    print("源地理信息："+str(src_trans))
    OriginLX_src = src_trans[0]
    OriginTY_src = src_trans[3]
    pixl_w_src = src_trans[1]
    pixl_h_src = src_trans[5]
    OriginRX_src = OriginLX_src + pixl_w_src * src_width
    OriginBY_src = OriginTY_src + pixl_h_src * src_height
    # 目标数据栅格投影
    dstSRS = osr.SpatialReference()
    # 这是一个在gdal3.0以上版本才会出现的问题
    # 如果不加下面的代码，使用osr.CoordinateTransformation.TransformPoint()的时候会出现这样的状况：
    # longitude,latitude,z=osr.CoordinateTransformation.TransformPoint(latitude,longitude)
    # 换言之就是返回的经纬度与输入的经纬度相反
    if int(osgeo.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        dstSRS.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    dstSRS.ImportFromEPSG(4326)
    # 投影转换
    ct = osr.CoordinateTransformation(srcSRS, dstSRS)
    # 计算目标影像的左上和右下坐标,即目标影像的仿射变换参数
    OriginLX_dst, OriginTY_dst, temp = ct.TransformPoint(OriginLX_src, OriginTY_src)
    OriginRX_dst, OriginBY_dst, temp = ct.TransformPoint(OriginRX_src, OriginBY_src)
    # 临时文件，因为不经过压缩以及金字塔构建的话文件太庞大以及难易读取
    gdal.Warp(os.path.join(dstpath,os.path.splitext(tiff)[0]+"_temp.tif"), src_data, format='GTiff',
              xRes=0.0003, yRes=0.0003, srcNodata=0, dstNodata=0,
              outputBounds=[OriginLX_dst, OriginBY_dst, OriginRX_dst, OriginTY_dst],
              outputType=gdal.GDT_Byte, resampleAlg=gdal.GRA_NearestNeighbour, targetAlignedPixels=False,
              srcSRS='EPSG:'+str(srcSRS.GetAttrValue("AUTHORITY", 1)), dstSRS='EPSG:4326')
    temp_data: gdal.Dataset=gdal.Open(os.path.join(dstpath,os.path.splitext(tiff)[0]+"_temp.tif"),gdalconst.GA_ReadOnly)
    temp_band: gdal.Band=temp_data.GetRasterBand(1)
    print(temp_data.GetGeoTransform())
    driver = gdal.GetDriverByName("GTiff")
    dst_data: gdal.Dataset=driver.Create(os.path.join(dstpath,tiff), xsize=temp_data.RasterXSize, ysize=temp_data.RasterYSize,
                                         bands=temp_data.RasterCount, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
    dst_data.SetGeoTransform(temp_data.GetGeoTransform())
    dst_data.SetProjection(temp_data.GetProjection())
    dst_band: gdal.Band=dst_data.GetRasterBand(1)
    dst_band.WriteArray(temp_band.ReadAsArray())
    dst_band.SetNoDataValue(0)
    dst_data.BuildOverviews("AVERAGE", overviewlist=[2, 4, 8, 16, 32, 64, 128])
    temp_data,temp_band=None,None
    os.remove(os.path.join(dstpath,os.path.splitext(tiff)[0]+"_temp.tif"))
    dst_data=None
    print(tiff+"处理完成")
# 方法二：使用osr计算不同投影下的坐标变换，之后写入数据
'''
for tiff in alltiff:
    print(tiff + "开始重投影")
    src_data: gdal.Dataset = gdal.Open(os.path.join(inpath, tiff), gdalconst.GA_ReadOnly)
    # 获取源数据坐标信息并转换格式
    srcSRS_wkt = src_data.GetProjection()
    srcSRS = osr.SpatialReference()
    # 这是一个在gdal3.0以上版本才会出现的问题
    # 如果不加下面的代码，使用osr.CoordinateTransformation.TransformPoint()的时候会出现这样的状况：
    # longitude,latitude,z=osr.CoordinateTransformation.TransformPoint(latitude,longitude)
    # 换言之就是返回的经纬度与输入的经纬度相反
    if int(osgeo.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        srcSRS.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    srcSRS.ImportFromWkt(srcSRS_wkt)
    # 获取源数据栅格尺寸
    src_width = src_data.RasterXSize
    src_height = src_data.RasterYSize
    src_bandcount = src_data.RasterCount
    # 获取源图像的仿射变换参数
    src_trans = src_data.GetGeoTransform()
    print("源地理信息："+str(src_trans))
    OriginLX_src = src_trans[0]
    OriginTY_src = src_trans[3]
    pixl_w_src = src_trans[1]
    pixl_h_src = src_trans[5]
    OriginRX_src = OriginLX_src + pixl_w_src * src_width
    OriginBY_src = OriginTY_src + pixl_h_src * src_height
    # 创建输出图像
    driver = gdal.GetDriverByName("GTiff")
    dst_data: gdal.Dataset=driver.Create(os.path.join(dstpath,tiff), xsize=src_width, ysize=src_height,
                                         bands=src_bandcount, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
    dstSRS = osr.SpatialReference()
    # 这是一个在gdal3.0以上版本才会出现的问题
    # 如果不加下面的代码，使用osr.CoordinateTransformation.TransformPoint()的时候会出现这样的状况：
    # longitude,latitude,z=osr.CoordinateTransformation.TransformPoint(latitude,longitude)
    # 换言之就是返回的经纬度与输入的经纬度相反
    if int(osgeo.__version__[0]) >= 3:
        # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
        dstSRS.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
    dstSRS.ImportFromEPSG(4326)
    # 投影转换
    ct = osr.CoordinateTransformation(srcSRS, dstSRS)
    # 计算目标影像的左上和右下坐标,即目标影像的仿射变换参数
    OriginLX_dst, OriginTY_dst, temp = ct.TransformPoint(OriginLX_src, OriginTY_src)
    OriginRX_dst, OriginBY_dst, temp = ct.TransformPoint(OriginRX_src, OriginBY_src)
    pixl_w_dst = (OriginRX_dst - OriginLX_dst) / src_width
    pixl_h_dst = (OriginBY_dst - OriginTY_dst) / src_height
    dst_trans = [OriginLX_dst, pixl_w_dst, 0, OriginTY_dst, 0, pixl_h_dst]
    print("WGS84地理信息："+str(dst_trans))
    # print outTrans
    dstSRS_wkt = dstSRS.ExportToWkt()
    # 设置仿射变换系数及投影
    dst_data.SetGeoTransform(dst_trans)
    dst_data.SetProjection(dstSRS_wkt)
    # 重新投影
    gdal.ReprojectImage(src_data, dst_data, srcSRS_wkt, dstSRS_wkt, gdal.GRA_NearestNeighbour)
    dst_band: gdal.Band=dst_data.GetRasterBand(1)
    dst_band.SetNoDataValue(255)
    dst_data.BuildOverviews("AVERAGE", overviewlist=[2, 4, 8, 16, 32, 64, 128])
'''
