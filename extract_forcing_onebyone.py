# before running this, need to authenticate
# %run desp-authentication.py
#
# ACTIVATE ENVIRONMENT
# export PATH="/projappl/project_2010748/DTO4OWE/earthkit/bin:$PATH"
#
from polytope_zarr import PolytopeZarrStore
from earthkit.regrid import interpolate
from datetime import timedelta
import datetime
from calendar import monthrange
import numpy as np
from sys import argv
#
#
model = "IFS-NEMO"
if len(argv)>0:
    year  = int(argv[1])
else:
    year  = 1990
#
#list of forcing variables we need

# daily boundary variables
boundary_variables = {'avg_thetao':{'stream':'clte','levtype':'o3d','freq':'daily'},
                      'avg_so':{'stream':'clte','levtype':'o3d','freq':'daily'},
                      'avg_uoe':{'stream':'clte','levtype':'o3d','freq':'daily'},
                      'avg_von':{'stream':'clte','levtype':'o3d','freq':'daily'},
                      'avg_zos':{'stream':'clte','levtype':'o2d','freq':'daily'},
}

#hourly forcing variables
forcing_variables = {'2t':{'stream':'clte','levtype':'sfc','freq':'hourly'},
                     '2d':{'stream':'clte','levtype':'sfc','freq':'hourly'},
                     'sp':{'stream':'clte','levtype':'sfc','freq':'hourly'}, #surface pressure (is this at 2m?)
                     'msl':{'stream':'clte','levtype':'sfc','freq':'hourly'}, #sea level pressure
                     '10u':{'stream':'clte','levtype':'sfc','freq':'hourly'},
                     '10v':{'stream':'clte','levtype':'sfc','freq':'hourly'},
                     'avg_sdlwrf':{'stream':'clte','levtype':'sfc','freq':'hourly'}, #downward longwave
                     'avg_sdswrf':{'stream':'clte','levtype':'sfc','freq':'hourly'}, #downward shortwave
                     'avg_tprate':{'stream':'clte','levtype':'sfc','freq':'hourly'}, #time mean precip kg m-2 s-1
                     'avg_tsrwe':{'stream':'clte','levtype':'sfc','freq':'hourly'}, #Time-mean total snowfall rate water equivalent
}

area_NSBS = (66,-4.5,48.4,30.5)
# ######################################################################################
#LEVTYPE = "sfc"                    # 34 vars — surface (14 instant + 20 hourly mean)
# LEVTYPE = "pl"                   #  9 vars — pressure levels (19 levels)
# LEVTYPE = "hl"                   #  2 vars — height levels (100 m, IFS-only)
# LEVTYPE = "sol"                  #  2 vars — soil / snow
# LEVTYPE = "o2d"                  # 12 vars — 2-D ocean & sea ice (daily)
# LEVTYPE = "o3d"                  #  5 vars — 3-D ocean (daily, up to 75 levels)
# #####################################################################################
#
#
exp_dates={'hist':{'start':"1990-01-01T00:00:00",'end':"2014-12-31T23:00:00"},
           'ssp3-7.0':{'start':"2015-01-01T00:00:00",'end':"2049-12-31T23:00:00"}
}
ssp370_start_date = datetime.date.fromisoformat(exp_dates['ssp3-7.0']['start'][:10])
#
if year>=ssp370_start_date.year:
    exp='ssp3-7.0'
else:
    exp='hist'

outpath='/scratch/project_2010748/DTO4OWE/CLIMATE_DT/'
# maybe it would be faster to download by 
#
store={}
store['sfc_hourly'] = PolytopeZarrStore.from_climate_dt(
            models=[model],
            experiment=exp,
            resolution="high", # 'standard', 'high'
            levtype='sfc',
            frequency='hourly',
            start_date=exp_dates[exp]['start'],
            end_date=exp_dates[exp]['end']
        )
store['o3d_daily'] = PolytopeZarrStore.from_climate_dt(
            models=[model],
            experiment=exp,
            resolution="high",
            levtype='o3d',
            frequency='hourly', #apparently needs to be hourly even for daily data...
            start_date=exp_dates[exp]['start'],
            end_date=exp_dates[exp]['end']
        )
store['o2d_daily'] = PolytopeZarrStore.from_climate_dt(
            models=[model],
            experiment=exp,
            resolution="high",
            levtype='o2d',
            frequency='hourly',
            start_date=exp_dates[exp]['start'],
            end_date=exp_dates[exp]['end']
        )

############################
# download surface forcing #
############################
#
# list all the variables that we are going to download
fvariables=list(forcing_variables.keys())
# open zarr
ds = store['sfc_hourly'].open()
#start_date = datetime.date.fromisoformat(exp_dates[exp]['start'][:10])
#end_date   = datetime.date.fromisoformat(exp_dates[exp]['end'][:10])
#for year in range(start_date.year,end_data.year+1,1):
# download month by month
for var in fvariables:
    encoding={}
    encoding[var]={"zlib": True, "complevel": 5}
    for month in range(1,13):
        print(year,month)
        days_in_month = monthrange(year,month)[1]
        timeslice=slice(str(year)+"-"+str(month).zfill(2)+"-01T00:00", str(year)+"-"+str(month).zfill(2)+"-"+str(days_in_month).zfill(2)+"T23:00")
        #the following took 8 minutes - extracting 10 years of data for one variable would mean 16 hours - probably okay
        ds_latlon = ds[var].polytope.sel(model=model,time=timeslice,area=area_NSBS,grid="0.05/0.05")
        outfile   = outpath+model+'/'+exp+'/sfc_'+var+'_'+model+'_'+exp+'_'+str(year)+'_'+str(month).zfill(2)+'.nc'
        # remove problematic attributes
        del ds_latlon[var].attrs['_earthkit']
        # save the data to disk
        ds_latlon.to_netcdf(outfile,format="NETCDF4",unlimited_dims='time',encoding=encoding)
    #data = earthkit.data.from_source("polytope", "destination-earth", request2, address="polytope.mn5.apps.dte.destination-earth.eu", stream=False)
    #data2.to_target("file", data_file2)
    # Regrid t=from healpix for conversion to xarray
    #data_latlon = earthkit.regrid.interpolate(data, out_grid={"grid": [1,1]}, method="linear")
    # Convert data to xarray
    #ds_latlon.to_xarray().to_netcdf(outfile)

#############################
# DOWNLOAD BOUNDARY FORCING #
# ######################### #
#
if False:
    N=10
    lons   = np.linspace(-5, 10, N)
    lats   = np.ones(N)*60
    depths = np.ones(N)
    pts    = np.stack([lats, lons, depths], axis=1)
    #
    request = {
        "activity": "projections",
        "class": "d1",
        "dataset": "climate-dt",
        "experiment": "ssp3-7.0",
        "generation": "2",
        "levtype": "o3d",
        "date": "20400102",
        "model": "ifs-nemo",
        "expver": "0001",
        "param": "avg_thetao",
        "realization": "1",
        "resolution": "standard",
        "stream": "clte",
        "type": "fc",
        "time": "0000",
        "feature" :{
            "type" : "trajectory",
            "points" : pts.tolist(),
            "inflation" : [0.1,0.1,10],
            "inflate" : "box",
            "axes" :["latitude", "longitude","levelist"],
        },
    }
    # get the data along a trajectory. This kind of works, but does not return the depth axis here.
    ocena_traj = earthkit.data.from_source("polytope", "destination-earth", request, address="polytope.mn5.apps.dte.destination-earth.eu", stream=False)

#d0.polytope.sel(model='IFS-NEMO',time=slice('2014-01-01','2014-01-31'),level=1,point=(62,18))
#
#bbox_result = d0.polytope.sel(
#    model="IFS-NEMO",
#    time=slice('2014-01-01','2014-01-31')
#    bbox=(62, 18, 62.05, 18.5),  # (south, west, north, east)
#)

