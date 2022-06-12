import netCDF4 as nc
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeat
import matplotlib.ticker as mticker
import cmaps,os
import numpy as np
from datetime import datetime,timedelta
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from matplotlib.font_manager import FontProperties

ncfile=nc.Dataset(r"D:\era5-gzj0623.nc")
print(ncfile.variables.keys())

f=ncfile["sp"][:,36,46]
f=f-273.15
#f=f/(3600)
print(f)

#f[36,46]=0
'''
i=4
f=ncfile["sst"][i,:,:]
x=ncfile["longitude"]
y=ncfile["latitude"]
quiver_interval=1
fig = plt.figure(figsize=(5, 5))
axe = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
#axe.set_extent([start_lon, end_lon, start_lat, end_lat], crs=ccrs.PlateCarree())
#axe.set_title(str(now_date) + " " + var, y=1.1, fontsize=12, fontproperties=FontProperties(fname="../font/Times.ttf"))
gl = axe.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color="gray", linestyle=":")
gl.top_labels, gl.bottom_labels, gl.right_labels, gl.left_labels = False, True, False, True
#gl.xlocator = mticker.FixedLocator(np.arange(start_lon, end_lon, lonlat_interval))
#gl.ylocator = mticker.FixedLocator(np.arange(start_lat, end_lat, lonlat_interval))
axe.add_feature(cfeat.COASTLINE.with_scale("10m"), linewidth=1, color="k", zorder=1)
contourf = axe.contourf(ncfile["longitude"][:], ncfile["latitude"][:], f,
                        cmap=cmaps.ncl_default, extend="neither", zorder=0)
ws1, ws2 = ncfile["u10"][i, :, :][::quiver_interval,::quiver_interval], ncfile["v10"][i, :, :][::quiver_interval,::quiver_interval]
lat, lon = y[::quiver_interval], x[::quiver_interval]
quiver = axe.quiver(lon, lat, ws1, ws2, pivot='mid',width=0.002, scale=150,transform=ccrs.PlateCarree())
# 绘制矢量箭头的图例
axe.quiverkey(quiver, 0.95, 1.05, 3, "3m/s",
              labelpos='E', coordinates='axes')
fig.subplots_adjust(right=0.85)
rect = [0.9, 0.1, 0.02, 0.8]  # 分别代表，水平位置，垂直位置，水平宽度，垂直宽度
cbar_ax = fig.add_axes(rect)
cb = fig.colorbar(contourf, drawedges=True, cax=cbar_ax, orientation="vertical", spacing='uniform')  # orientation='vertical'
fig.show()
plt.show()
'''