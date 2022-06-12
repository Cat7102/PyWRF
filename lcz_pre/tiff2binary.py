# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-03-26 01:28:26
# @Desc  : 本文件用于将tiff文件转换为binary文件

from osgeo import gdal
import os

def landuse2binary_file(tiff_file, bil_folder):
    options_list = ['-of ENVI']
    options_string = " ".join(options_list)

    print("开始转换" + tiff_file)

    tiff_data = gdal.Open(tiff_file)
    # 栅格矩阵的列数
    tif_columns = tiff_data.RasterXSize
    # 栅格矩阵的行数
    tif_nrows = tiff_data.RasterYSize

    gdal.Translate(os.path.join(bil_folder , "00001" + "-" + str(tif_columns).zfill(5) + "." + "00001" + "-" + str(tif_nrows).zfill(5)), tiff_file,
                   options=options_string)
    print(os.path.join(bil_folder , "00001" + "-" + str(tif_columns).zfill(5) + "." + "00001" + "-" + str(tif_nrows).zfill(5)) + "文件编译完成")

if __name__ == '__main__':
    #landuse2binary_file("LCZC_Tsing2017_100m_wgs84.tif", "./")
    landuse2binary_file("LCZC_globeland30_100m_wgs84.tif", "./")
