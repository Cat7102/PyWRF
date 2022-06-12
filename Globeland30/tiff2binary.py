# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-24 20:15:12
# @Desc  : 将globeland30数据转为binary文件

from osgeo import gdal,gdalconst
import os

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

def tiff2binary_folder(folder,tiff_base,N_lat,S_lat,W_lon,E_lon):
    for lat in range(N_lat,S_lat-10,-10):
        for lon in range(W_lon,E_lon+10,10):
            tiff: gdal.Dataset=gdal.Open(os.path.join(folder,tiff_base+"lat{}lon{}.tif".format(lat,lon)),gdalconst.GA_ReadOnly)
            tiff2binary(os.path.join(folder,tiff_base+"lat{}lon{}.tif".format(lat,lon)),
                        start_x=int((lon-W_lon)/10*tiff.RasterXSize+1),start_y=int((N_lat-lat)/10*tiff.RasterYSize+1),
                        outfolder=r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\6.Binary\Globeland30_2020_500m")
            geo = tiff.GetGeoTransform()
            print(geo)

if __name__ == '__main__':
    tiff2binary_folder(r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\Globeland30_2020\5.Cropped_Resampled_Reclassified\resampled&reclassified_500m",
                       "reclassified_globeland30_2020_",60,30,70,130)
