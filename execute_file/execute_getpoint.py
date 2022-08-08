# -*- coding: utf-8 -*-
# @Author: cat
# @Date  : 2022-08-06 20:08:14
# @Desc  : 用于提取WRF输出结果中特定点的数据，必须具有四个维度——高度、时间、经度、纬度，默认使用的配置文件为namelist_getpoint.py

import os
import pandas as pd
from namelist_getdpoint import *
import netCDF4 as nc
from wrf import getvar, to_np, ALL_TIMES
from lib.Readtime import get_ncfile_time
import numpy as np
from lib.Readheight import get_ncfile_point_height2earth_index

def save_file(name,mode,data):
    data_df=pd.DataFrame(data)
    if mode=="csv":
        data_df.to_csv(name+".csv",index=False,header=False)
    if mode=="xlsx":
        writer=pd.ExcelWriter(name+".xlsx")
        data_df.to_excel(writer,"sheet",index=False,header=False)
        writer.save()
    print("{}文件保存完成".format(name))

ncfile=nc.Dataset(ncfilename)
timelist=get_ncfile_time(ncfile,timezone=timezone)[time_s:time_e][::time_st]
timelist=np.array(timelist)
var_ndarray=to_np(getvar(ncfile,var,timeidx=time_s))[:,index_lat,index_lon][np.newaxis,:] # 需要将数组变为二维
for i in range(time_s+1,time_e, time_st):
    print(i)
    var_ndarray=np.append(var_ndarray,to_np(getvar(ncfile,var,timeidx=i))[:,index_lat,index_lon][np.newaxis,:],axis=0)
if extra_var != None: # 处理低于eta层的数据
    if extra_var=="T2":
        extra_var_ndarray=to_np(getvar(ncfile,extra_var,timeidx=ALL_TIMES))[time_s:time_e,index_lat,index_lon]-273.15
    else:
        extra_var_ndarray = to_np(getvar(ncfile, extra_var, timeidx=ALL_TIMES))[time_s:time_e, index_lat,index_lon]
    extra_var_ndarray = extra_var_ndarray[::time_st]
    print(np.shape(var_ndarray),np.shape(extra_var_ndarray))
    all_data=np.append(extra_var_ndarray[:,np.newaxis],var_ndarray,axis=1) # 数据合成
else:
    all_data=var_ndarray # 数据名统一
del var_ndarray # 释放内存
all_data=np.around(all_data,decimals=precision)
all_data=np.append(timelist[:,np.newaxis],all_data,axis=1)
savefilename="lat_"+str(index_lat)+"_lon_"+str(index_lon)+"_"+var+"_"+str(precision)+"precision"
save_file(savefilename,savemode,all_data.T)
h2e = get_ncfile_point_height2earth_index(ncfilename, index_lat,index_lon)
print("离地高度为：")
for i in range(h2e.shape[0]):
    print(str(h2e[i]),end=",")