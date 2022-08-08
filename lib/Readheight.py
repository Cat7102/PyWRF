from wrf import getvar,to_np,ll_to_xy
import netCDF4 as nc

def get_ncfile_point_height(path,point_lat,point_lon):
	ncfile=nc.Dataset(path)
	y, x = ll_to_xy(ncfile, point_lat, point_lon)
	height = to_np(getvar(ncfile, "height"))[:, x, y]
	return height

def get_ncfile_point_pressure(path,point_lat,point_lon):
	ncfile=nc.Dataset(path)
	y, x = ll_to_xy(ncfile, point_lat, point_lon)
	pressure = to_np(getvar(ncfile, "pressure"))[:, x, y]
	return pressure

def get_ncfile_point_height2earth(path,point_lat,point_lon):
	ncfile=nc.Dataset(path)
	y, x = ll_to_xy(ncfile, point_lat, point_lon)
	hgt = ncfile.variables['HGT'][0, x, y]
	height = to_np(getvar(ncfile, "height"))[:, x, y]
	h2e=height-hgt
	return h2e

def get_ncfile_point_height_index(path,index_lat,index_lon):
	ncfile=nc.Dataset(path)
	height = to_np(getvar(ncfile, "height"))[:, index_lon, index_lat]
	return height

def get_ncfile_point_pressure_index(path,index_lat,index_lon):
	ncfile=nc.Dataset(path)
	pressure = to_np(getvar(ncfile, "pressure"))[:, index_lon, index_lat]
	return pressure

def get_ncfile_point_height2earth_index(path,index_lat,index_lon):
	ncfile=nc.Dataset(path)
	hgt = ncfile.variables['HGT'][0, index_lon, index_lat]
	height = to_np(getvar(ncfile, "height"))[:, index_lon, index_lat]
	h2e=height-hgt
	return h2e

