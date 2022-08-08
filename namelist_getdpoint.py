# -*- coding: utf-8 -*-
# @Author: cat
# @Date  : 2022-08-07 22:28:21
# @Desc  : 用于数据提取的namelist文件，设置参数后执行文件在execute_file中

ncfilename = r'D:\Data\WRF-Chem_Files\WRF-Chem_Simulation\LCZ_2021_Jul_HighTemp\wrfout_d03_2021-07-09_00-00-00'  # .nc文件的地址
timezone = 8  # 设置时区
index_lat,index_lon = 97,89 # 提取数据点的经纬度序列号
time_s,time_e,time_st = 264, 337, 3 # 数据的起止时间
var = "ua"  # 提取的变量名
extra_var = "U10" # 如温度、风速等除了eta层以外还包括一个最底层的基础数据，例如两米温度与10米风速等。如不需要改为None
precision = 2  # 数据精度，x表示保留x位小数
savefolder = r'./'  # 文件保存到的文件夹
savemode = "csv"  # 可以选择csv或者xlsx格式
