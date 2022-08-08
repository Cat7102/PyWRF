# -*- coding: utf-8 -*-
# @Author: Piero
# @Date  : 2022-08-02 16:43:51
# @Desc  : 本脚本仅用于ERA5 Hourly数据的简单绘制

import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import netCDF4 as nc
import numpy as np
import cmaps

# ERA5数据存储地址
era5_path=r"D:\Data\CFD_Files\CFD_Project_File\ERA5数据\Sh_20210710-20210715_era5_hourly.nc"

# 数据读取部分
ncfile=nc.Dataset(era5_path)
lon, lat = ncfile["longitude"][:], ncfile["latitude"][:]
print(lon,lat)
min_lat, max_lat = np.round(np.min(lat), 2), np.round(np.max(lat), 2)
min_lon, max_lon = np.round(np.min(lon), 2), np.round(np.max(lon), 2)
t2=ncfile["t2m"][0,...]
# 绘图部分
fig = plt.figure(figsize=(10, 10))
axe_contour = plt.subplot(1, 2, 1, projection=ccrs.PlateCarree())
axe_point = plt.subplot(1, 2, 2, projection=ccrs.PlateCarree())
# contour绘图
axe_contour.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k",zorder=1)
axe_contour.set_extent([min_lon-0.25, max_lon+0.25, min_lat-0.25, max_lat+0.25],crs=ccrs.PlateCarree())
gl = axe_contour.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
gl.xlocator = mticker.FixedLocator(np.arange(min_lon-0.25, max_lon+0.25, np.round((max_lon - min_lon) / 5, 2)))
gl.ylocator = mticker.FixedLocator(np.arange(min_lat-0.25, max_lat+0.25, np.round((max_lat - min_lat) / 5, 2)))
contourf = axe_contour.contourf(lon, lat, t2, cmap=cmaps.matlab_hot_r, extend="neither", zorder=0)
# plot绘图
axe_point.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k",zorder=1)
axe_point.set_extent([min_lon-0.25, max_lon+0.25, min_lat-0.25, max_lat+0.25],crs=ccrs.PlateCarree())
gl = axe_point.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon+0.25, 0.25))
gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat+0.25, 0.25))
for lo in lon:
    for la in lat:
        axe_point.plot(lo,la,"o")
        axe_point.text(lo,la+0.03,"("+str(int((max_lat-la)/0.25))+","+str(int((lo-min_lon)/0.25))+")",horizontalalignment="center",fontsize=8)
# 展示
fig.show()
plt.show()