# -*- coding: utf-8 -*-
# @Author: Fishercat
# @Date  : 2022-05-18 17:34:08
# @Desc  : 使用HEG_TOOLS将hdf文件转换为tiff文件

import os
from osgeo import gdal

def create_prm(hdffile,band,inpath,outpath):
    '''
    @param index: 卫星图的行列号，比如h29v06
    @param band: 由于模拟需要，只取Fpar_500m, Lai_500m和FparLai_QC
    '''
    datasets = gdal.Open(os.path.join(inpath,hdffile))
    #  获取hdf中的元数据
    Metadata = datasets.GetMetadata()
    #  获取四个角的经纬度
    NorthLatitudes = Metadata["NORTHBOUNDINGCOORDINATE"]
    WestLongitude = Metadata["WESTBOUNDINGCOORDINATE"]
    SouthLatitudes = Metadata["SOUTHBOUNDINGCOORDINATE"]
    EastLongitude = Metadata["EASTBOUNDINGCOORDINATE"]
    prm = ['NUM_RUNS = 1\n',
           'BEGIN\n',
           'INPUT_FILENAME = ' + os.path.join(inpath,hdffile) + '\n',
           'OBJECT_NAME = MOD_Grid_MOD15A2H|\n',
           'FIELD_NAME = '+band+'\n',
           'BAND_NUMBER = 1\n',
           'SPATIAL_SUBSET_UL_CORNER = ( '+str(NorthLatitudes)+' '+str(WestLongitude)+' )\n',
           'SPATIAL_SUBSET_LR_CORNER = ( '+str(SouthLatitudes)+' '+str(EastLongitude)+' )\n',
           'RESAMPLING_TYPE = BI\n',
           'OUTPUT_PROJECTION_TYPE = GEO\n',
           'ELLIPSOID_CODE = WGS84\n',
           'OUTPUT_PROJECTION_PARAMETERS =  ( 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0  )\n',
           'OUTPUT_PIXEL_SIZE = 15.0000238906\n',
           'OUTPUT_FILENAME = ' + os.path.join(outpath,hdffile.split(".")[1]+"_"+hdffile.split(".")[2]+"_"+band+".tif") + '\n',
           'OUTPUT_TYPE = GEO\n',
           'END\n']
    prmfilename = os.path.join(prmpath,hdffile.split(".")[1]+"_"+hdffile.split(".")[2]+"_"+band+".prm")
    print("Create PRM file: {}".format(prmfilename))
    # it is important to note here that the newline character is set to ‘\n’, otherwise by windows \r\n,
    fo = open(prmfilename, 'w', newline='\n')
    fo.writelines(prm)
    fo.close()

#  set the heg-related environment variables
os.environ['MRTDATADIR'] = r'C:\Application\HEG\HEG_Win\data'
os.environ['PGSHOME'] = r'C:\Application\HEG\HEG_Win\TOOLKIT_MTD'
os.environ['MRTBINDIR'] = r'C:\Application\HEG\HEG_Win\bin'

#  set the heg bin the path
hegpath = r'C:\Application\HEG\HEG_Win\bin'
#  specifies an executable program file path for the processing module, as used here resample.exe， can be set according to the specific processing problem
hegdo = os.path.join(hegpath, 'resample.exe')
# specifies the path to the input data
# 文件需要分文件夹进行放置，例如2021_Origin\01\MCD15A2H.A2020... , 2021_Origin\02\MCD15A2H.A2021... , 2021_Origin\03\MCD15A2H.A2021...
inpath_root = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_1.Origin'
#  specifies the path to the output data
outpath_root = r'D:\Data\WRF-Chem_Files\LAI_FPAR\2021_2.GeoTiff'
# os.chdir(inpath) # change the current working directory to the input data directory
# prm file setup module needs to be first in HEG a reference prm file is generated in the tool ， the sample is as follows
#  set the prm file storage path
prmpath = r"D:\Data\WRF-Chem_Files\LAI_FPAR\2021_1.Origin\PRM"

# 十二个月循环
for month in range(1,13,1):
    month=str(month).zfill(2) # 月份需要保持两位数
    inpath=os.path.join(inpath_root,month) # 将inpath_root与月份合成
    #  gets all the hdf files in the current folder
    allfiles = os.listdir(inpath)
    allhdffiles = []
    for eachfile in allfiles:
        if os.path.splitext(eachfile)[1] =='.hdf':
            allhdffiles.append(eachfile)
    # 如果outpath根目录下没有分月份的文件夹，则创建
    if not os.path.exists(os.path.join(outpath_root,inpath.split("\\")[-1])):
        print("Create Folder：{}".format(os.path.join(outpath_root,inpath.split("\\")[-1])))
        os.makedirs(os.path.join(outpath_root,inpath.split("\\")[-1]))
    outpath=os.path.join(outpath_root,inpath.split("\\")[-1]) # 将outpath与月份结合

    # 输出头信息
    print('--' * 20)
    print(' the number of files is :', len(allhdffiles), ', all hdf files are as follows ')
    print('  ' + '\n  '.join(allhdffiles))
    print('--' * 20)

    for eachhdf in allhdffiles:
        print("Source hdf4 file: {}".format(os.path.join(inpath,eachhdf)))
        index=eachhdf.split(".")[1]+"_"+eachhdf.split(".")[2]
        # 创建prm文件
        create_prm(eachhdf,"Lai_500m",inpath,outpath)
        create_prm(eachhdf,"Fpar_500m",inpath,outpath)
        create_prm(eachhdf,"FparLai_QC",inpath,outpath)
        prmfilepath_LAI = os.path.join(prmpath,index+"_Lai_500m.prm")
        prmfilepath_FPAR = os.path.join(prmpath,index+"_Fpar_500m.prm")
        prmfilepath_QC = os.path.join(prmpath,index+"_FparLai_QC.prm")
        try:
            # hdf4转geotiff是通过系统调用heg_tools中的resample.exe
            resamplefiles = '{0} -P {1}'.format(hegdo, prmfilepath_LAI)
            os.system(resamplefiles)
            print(eachhdf + ' has finished')
            resamplefiles = '{0} -P {1}'.format(hegdo, prmfilepath_FPAR)
            os.system(resamplefiles)
            print(eachhdf + ' has finished')
            resamplefiles = '{0} -P {1}'.format(hegdo, prmfilepath_QC)
            os.system(resamplefiles)
            print(eachhdf + ' has finished')
            print('==' * 40)
        except:
            print(eachhdf + 'was wrong')
