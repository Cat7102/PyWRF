import gdal
import numpy as np

a=gdal.Open(r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\7_CombineTsinghua2017\LCZCold_globeland30_100m_wgs84.tif")
data=a.GetRasterBand(1)
value=data.ReadAsArray()
value[np.where(value==21)]=17
driver = gdal.GetDriverByName("GTiff")
edt_tiff: gdal.Dataset = driver.Create(r"D:\Data\WRF-Chem_Files\LandUse_LandCover_Data\LCZ_Shanghai_2021\Landsat8\7_CombineTsinghua2017\LCZC_globeland30_100m_wgs84.tif",
                                       xsize=a.RasterXSize, ysize=a.RasterYSize,
                                       bands=1, eType=gdal.GDT_Byte, options=["TILED=YES", "COMPRESS=LZW"])
edt_band: gdal.Band = edt_tiff.GetRasterBand(1)
edt_tiff.SetProjection(a.GetProjection())
edt_tiff.SetGeoTransform(a.GetGeoTransform())
edt_band.WriteArray(value)
edt_band.SetNoDataValue(0)
edt_tiff.FlushCache()
edt_tiff.GetRasterBand(1).ComputeStatistics(True)