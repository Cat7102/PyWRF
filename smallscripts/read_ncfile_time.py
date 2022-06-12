#这个脚本仅用于读取时间

import netCDF4 as nc
from lib.Readtime import get_ncfile_time

#仅需要修改一下文件的路径即可
path=r'D:\Data\WRF-Chem_Files\WRF-Chem_Simulation\lcz_2021_07\wrfout_d03_2021-07-12'
ncfile=nc.Dataset(path)
timelist=get_ncfile_time(ncfile=ncfile)
for i in range(len(timelist)):
    print("["+str(i)+"]"+timelist[i])