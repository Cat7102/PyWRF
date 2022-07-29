# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-07-19 19:59:51
# @Desc  : 用于geogrid生成文件的各个变量绘制

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.ticker as mticker
import numpy as np
import matplotlib.colors as c
from matplotlib.font_manager import FontProperties
from wrf import getvar
import netCDF4 as nc
import cmaps


def draw_landuse(min_lat, max_lat, min_lon, max_lon, axe, lat, lon, lu):
    axe.set_title("Landuse Map")
    level = {1: "1", 2: "2", 5: "5", 6: "6", 7: "7", 10: "10", 11: "11", 12: "12", 13: "13", 14: "14",
             15: "15", 16: "16", 17: "17", 19: "19", 20: "20", 31: "31", 32: "32", 33: "33", 34: "34",
             35: "35", 36: "36", 37: "37", 38: "38", 39: "39", 40: "40", 41: "41"}
    # 坐标绘制
    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
    gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
    gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon, np.round((max_lon - min_lon) / 5,2)))
    gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat, np.round((max_lat - min_lat) / 5,2)))
    # lu绘制
    classification = np.unique(lu)  # 获得本张图内涉及的土地利用分类
    classification = classification.astype(int)
    print(classification)
    for i in range(len(classification)):
        lu[np.where(lu == classification[i])] = i
    cmap = cmaps.circular_2
    axe.pcolormesh(lon, lat, lu, cmap=cmap, shading="auto", rasterized=True, zorder=0)
    # 绘制colorbar
    cmap_list = cmap(np.linspace(0, 1, len(classification)))
    proxy = [plt.Rectangle((0, 0), 1, 1, fc=i) for i in cmap_list]
    legend_lu = plt.legend(proxy, [level[i] for i in classification], loc="upper right", bbox_to_anchor=(1.12, 1),
                    labelspacing=0.5,handletextpad=0.2,handlelength=1, prop=FontProperties(size=9))
    axe.add_artist(legend_lu)

def draw_soiltop(min_lat, max_lat, min_lon, max_lon, axe, lat, lon, soiltop):
    axe.set_title("SoilType Top Map")
    level = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10,
             11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16}
    # 坐标绘制
    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
    gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
    gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon, np.round((max_lon - min_lon) / 5,2)))
    gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat, np.round((max_lat - min_lat) / 5,2)))
    # lu绘制
    classification = np.unique(soiltop)  # 获得本张图内涉及的土地利用分类
    classification = classification.astype(int)
    print(classification)
    for i in range(len(classification)):
        soiltop[np.where(soiltop == classification[i])] = i
    cmap = cmaps.circular_2
    axe.pcolormesh(lon, lat, soiltop, cmap=cmap, shading="auto", rasterized=True, zorder=0)
    # 绘制colorbar
    cmap_list = cmap(np.linspace(0, 1, len(classification)))
    proxy = [plt.Rectangle((0, 0), 1, 1, fc=i) for i in cmap_list]
    legend_lu = plt.legend(proxy, [level[i] for i in classification], loc="upper right", bbox_to_anchor=(1.12, 1),
                    labelspacing=0.7,handletextpad=0.2,handlelength=1, prop=FontProperties(size=9))
    axe.add_artist(legend_lu)

def draw_soiltemp(min_lat, max_lat, min_lon, max_lon, figure, axe, lat, lon, soiltemp):
    axe.set_title("Soil Temperature Map")
    axe.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k",zorder=1)
    # 坐标绘制
    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
    gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
    gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon, np.round((max_lon - min_lon) / 5,2)))
    gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat, np.round((max_lat - min_lat) / 5,2)))
    # lai绘制
    contourf = axe.contourf(lon, lat, soiltemp, cmap=cmaps.matlab_hot_r, extend="neither", zorder=0)
    figure.colorbar(contourf, ax=axe)  # orientation='vertical'

def draw_hgt(min_lat, max_lat, min_lon, max_lon, figure, axe, lat, lon, hgt):
    axe.set_title("HGT Map")
    axe.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k",zorder=1)
    # 坐标绘制
    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
    gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
    gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon, np.round((max_lon - min_lon) / 5,2)))
    gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat, np.round((max_lat - min_lat) / 5,2)))
    # lai绘制
    contourf = axe.contourf(lon, lat, hgt, cmap=cmaps.MPL_jet, extend="neither", zorder=0)
    figure.colorbar(contourf, ax=axe)  # orientation='vertical'

def draw_lai(min_lat, max_lat, min_lon, max_lon, figure, axe, lat, lon, lai):
    axe.set_title("Lai Map")
    axe.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k",zorder=1)
    # 坐标绘制
    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
    gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
    gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon, np.round((max_lon - min_lon) / 5,2)))
    gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat, np.round((max_lat - min_lat) / 5,2)))
    # lai绘制
    contourf = axe.contourf(lon, lat, lai, cmap=cmaps.MPL_PuBuGn, extend="neither", zorder=0)
    figure.colorbar(contourf, ax=axe)  # orientation='vertical'

def draw_greenfrac(min_lat, max_lat, min_lon, max_lon, figure, axe, lat, lon, greenfrac):
    axe.set_title("FPAR Map")
    axe.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k",zorder=1)
    # 坐标绘制
    gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
    gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
    gl.xlocator = mticker.FixedLocator(np.arange(min_lon, max_lon, np.round((max_lon - min_lon) / 5,2)))
    gl.ylocator = mticker.FixedLocator(np.arange(min_lat, max_lat, np.round((max_lat - min_lat) / 5,2)))
    # lai绘制
    contourf = axe.contourf(lon, lat, greenfrac, cmap=cmaps.MPL_YlGn, extend="neither", zorder=0)
    figure.colorbar(contourf, ax=axe)  # orientation='vertical'

if __name__ == '__main__':
    geogrid_file_path="D:\\geo_em.d04.nc"
    geodata=nc.Dataset(geogrid_file_path)
    lon,lat=getvar(geodata,"XLONG_M").values,getvar(geodata,"XLAT_M").values
    min_lat,max_lat=np.round(np.min(lat),2),np.round(np.max(lat),2)
    min_lon,max_lon=np.round(np.min(lon),2),np.round(np.max(lon),2)
    landuse=geodata["LU_INDEX"][0]
    soiltop=geodata["SCT_DOM"][0]
    lai=geodata["LAI12M"][0,6,:,:]
    fpar=geodata["GREENFRAC"][0,6,:,:]
    soiltemp=geodata["SOILTEMP"][0]
    hgt=geodata["HGT_M"][0]
    fig = plt.figure(figsize=(10, 10))
    axe = plt.subplot(2, 3, 1, projection=ccrs.PlateCarree())
    draw_landuse(min_lat,max_lat,min_lon,max_lon,axe,lat,lon,landuse)
    axe2 = plt.subplot(2, 3, 2, projection=ccrs.PlateCarree())
    draw_soiltop(min_lat,max_lat,min_lon,max_lon,axe2,lat,lon,soiltop)
    axe3 = plt.subplot(2, 3, 3, projection=ccrs.PlateCarree())
    draw_soiltemp(min_lat,max_lat,min_lon,max_lon,fig,axe3,lat,lon,soiltemp)
    axe4 = plt.subplot(2, 3, 4, projection=ccrs.PlateCarree())
    draw_hgt(min_lat,max_lat,min_lon,max_lon,fig,axe4,lat,lon,hgt)
    axe5 = plt.subplot(2, 3, 5, projection=ccrs.PlateCarree())
    draw_lai(min_lat,max_lat,min_lon,max_lon,fig,axe5,lat,lon,lai)
    axe6 = plt.subplot(2, 3, 6, projection=ccrs.PlateCarree())
    draw_greenfrac(min_lat,max_lat,min_lon,max_lon,fig,axe6,lat,lon,fpar)
    plt.subplots_adjust(wspace=0.25)
    fig.show()
    plt.show()