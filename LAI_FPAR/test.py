from osgeo import gdal
import numpy as np
import os

datasets = gdal.Open(r"D:\Data\WRF-Chem_Files\LAI_FPAR\2021\01\MCD15A2H.A2020361.h27v06.061.2021012074054.hdf")

#  获取hdf中的元数据
Metadata = datasets.GetMetadata()
#  获取四个角的经纬度
NorthLatitudes = Metadata["NORTHBOUNDINGCOORDINATE"]
WestLongitude = Metadata["WESTBOUNDINGCOORDINATE"]
SouthLatitudes = Metadata["SOUTHBOUNDINGCOORDINATE"]
EastLongitude = Metadata["EASTBOUNDINGCOORDINATE"]
#  采用", "进行分割
#LongitudeList = Longitude.split(", ")
print(NorthLatitudes,SouthLatitudes,WestLongitude,EastLongitude)
print(Metadata)
subdata=datasets.GetSubDatasets()
print(subdata)
Geo=datasets.GetGeoTransform()
print(Geo)
#Data=gdal.Open(subdata[1][0])
#print(Data.ReadAsArray())