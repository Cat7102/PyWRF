# -*- coding: utf-8 -*-
# @Author: cat
# @Date  : 2022-08-06 20:08:14
# @Desc  : 用于提取WRF输出结果中特定点的数据，必须具有四个维度——高度、时间、经度、纬度。与普通的提取不同的是其将数据与某一高度的数据相除，从而得到的数值。
#          默认使用的配置文件为namelist_getpoint4extra.py。

import os
import pandas as pd
from namelist_getdpoint4extra import *
import netCDF4 as nc
from wrf import getvar, to_np, ALL_TIMES
from lib.Readtime import get_ncfile_time
import numpy as np
from lib.Readheight import get_ncfile_point_height2earth_index

def save_file(name,mode,data,precision):
    data_df=pd.DataFrame(data)
    if mode=="csv":
        data_df.to_csv(name+".csv",float_format=precision,index=False,header=False)
    if mode=="xlsx":
        writer=pd.ExcelWriter(name+".xlsx")
        data_df.to_excel(writer,"sheet",float_format=precision,index=False,header=False)
        writer.save()
    print("{}文件保存完成".format(name))

ncfile=nc.Dataset(ncfilename)
timelist=get_ncfile_time(ncfile,timezone=timezone)[time_s:time_e][::time_st]
timelist=np.array(timelist)
var_ndarray=to_np(getvar(ncfile,var,timeidx=time_s))[:,index_lat,index_lon]
# 如果是T2则由于单位的差异，因此需要减去273.15K
if extra_var=="T2":
    extra_var_ndarray=to_np(getvar(ncfile,extra_var,timeidx=time_s))[index_lat,index_lon]-273.15
else:
    extra_var_ndarray = to_np(getvar(ncfile, extra_var, timeidx=time_s))[index_lat, index_lon]
level_var_ndarray=np.append(extra_var_ndarray,var_ndarray) # 每一层的底层数据与eta数据合并
level_var_ndarray=level_var_ndarray/level_var_ndarray[0] # 将底层数据作为参考数据，其他数据除以最低层数据
level_var_ndarray=level_var_ndarray[np.newaxis,:]
all_data=level_var_ndarray
for i in range(time_s+time_st,time_e,time_st):
    print(i)
    var_ndarray = to_np(getvar(ncfile, var, timeidx=i))[:, index_lat, index_lon]
    # 如果是T2则由于单位的差异，因此需要减去273.15K
    if extra_var == "T2":
        extra_var_ndarray = to_np(getvar(ncfile, extra_var, timeidx=i))[index_lat, index_lon] - 273.15
    else:
        extra_var_ndarray = to_np(getvar(ncfile, extra_var, timeidx=i))[index_lat, index_lon]
    level_var_ndarray = np.append(extra_var_ndarray, var_ndarray)  # 每一层的底层数据与eta数据合并
    level_var_ndarray = level_var_ndarray / level_var_ndarray[0]  # 将底层数据作为参考数据，其他数据除以最低层数据
    level_var_ndarray = level_var_ndarray[np.newaxis, :]
    all_data=np.append(all_data,level_var_ndarray,axis=0) # 按行不断添加数据
all_data=np.append(timelist[:,np.newaxis],all_data,axis=1)
savefilename="lat_"+str(index_lat)+"_lon_"+str(index_lon)+"_"+var+"_extra"
save_file(savefilename,savemode,all_data.T,precision)
h2e = get_ncfile_point_height2earth_index(ncfilename, index_lat,index_lon)
print("相对离地高度为：")
for i in range(h2e.shape[0]):
    print(str(h2e[i]/extra_height),end=",")
