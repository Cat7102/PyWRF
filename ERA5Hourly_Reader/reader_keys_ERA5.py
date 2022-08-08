# -*- coding: utf-8 -*-
# @Author: Piero
# @Date  : 2022-08-02 16:43:51
# @Desc  : 用于ERA5数据的变量名读取

import netCDF4 as nc

# ERA5数据存储地址
era5_path=r"D:\Data\CFD_Files\CFD_Project_File\ERA5数据\Sh_20210710-20210715_era5_hourly.nc"

# 主体部分
ncfile=nc.Dataset(era5_path)
keys=ncfile.variables.keys()
print(keys)
print(ncfile["sp"][:,6,7])