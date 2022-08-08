import netCDF4 as nc
from wrf import to_np, getvar

from lib.Interpolate import interpolate
from lib.Readheight import get_ncfile_point_height, get_ncfile_point_pressure, get_ncfile_point_height2earth

path = r'D:\Data\WRF-Chem_Files\WRF-Chem_Simulation\LCZ_2021_Jul_HighTemp\wrfout_d03_2021-07-09_00-00-00'  # 这里改下路径
point_lat, point_lon = 31, 121  # 这里修改需要插值的坐标纬度和经度

height = get_ncfile_point_height(path, point_lat, point_lon)
pressure = get_ncfile_point_pressure(path, point_lat, point_lon)
h2e = get_ncfile_point_height2earth(path, point_lat, point_lon)
print("该层的海拔高度、离地高度以及压力分别是：")
for i in range(height.shape[0]):
    print("[" + str(i) + "]" + str(height[i]) + " , " + str(h2e[i]) + " , " + str(pressure[i]))
