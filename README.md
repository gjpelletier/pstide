# Puget Sound Tide Channel Model for Python

A Python module for prediction of tides within Puget Sound

Adapted from the pstide.py module for Python 2.x by David Finlayson

Modified to run in Python 3.x by Greg Pelletier

The Puget Sound Tide Channel Model was first published in the late 1980's:

[Lavelle, J. W., H. O. Mofjeld, et al. (1988)](https://github.com/gjpelletier/pstide/blob/main/Lavelle_et_al_1988.pdf). A multiply-connected channel
  model of tides and tidal currents in Puget Sound, Washington and a comparison
  with updated observations. Seattle, WA, Pacific Marine Environmental
  Laboratory: 103pp. NOAA Technical Memorandum ERL PMEL-84

# Warning

The pstide code is intended only to be used for research purposes -- it is not intended for navigation. The official tidal predictions of the United States are available from NOAA/NOS (https://tidesandcurrents.noaa.gov/tide_predictions.html)

# Installing pstide

If you are installing for the first time, or upgrading from a previous installation, enter the following with pip or !pip in your notebook or terminal:<br>
```
pip install git+https://github.com/gjpelletier/pstide.git --upgrade
```

# Example 1. Tides in Budd Inlet for the next 7 days

Copy/paste and run the following in Jupyter Notebook to produce the output and figure below showing the next 7 days of tides in Budd Inlet segment 44. This example shows how to specify the segment number. The default time period (length) of the tide predictions is 7 days. The default starting datetime is the current time. The tide predictions at the selected location are stored in the result dictionary as a pandas dataframe in result['tides_selected_segment'].
```
from pstide import run_pstide
result = run_pstide(segment=44)
```
The following output is produced:
```
Calculating tides...

Puget Sound Tide Model: Tide Predictions

Segment Index: 44 (Budd_Inlet)
Longitude: -122.902685  Latitude: 47.056320
Minor constituents inferred from seattle.hcs
Starting time: 2025-08-01 01:59 UTC
Time step: 60.00 min  Length: 7.00 days
Mean water level: 2.53 m

Predictions generated: Thu Jul 24 19:29:47 2025 (System)
Heights in meters above MLLW
Prediction date and time in Pacific Time (PST or PDT)
```
<img width="2552" height="1639" alt="pstide_selected_segment" src="https://github.com/user-attachments/assets/84891d10-4e7b-4e88-9be5-090c0def0dee" />

# Example 2. Tides at a specified longitide and latitude

Copy/paste and run the following in Jupyter Notebook to produce the figure below showing the tides closest to lon=-122.615 and lat=47.885 in August 2025. This example shows how to specify the longitude (lon), latitude (lat), the starting datetime in ISO format, the time period (length) of the tide predictions, and how to use pacific=False to use datetimes in UTC. The tide predictions at the selected location are stored in the result dictionary as a pandas dataframe in result['tides_selected_segment'].
```
from pstide import run_pstide
result = run_pstide(lon=-122.615, lat=47.885, start='2025-08-01', length=31, pacific=False)
```
The following output is produced:
```
Calculating tides...

Puget Sound Tide Model: Tide Predictions

Segment Index: 518 (Hood_North)
Longitude: -122.594790  Latitude: 47.872545
Minor constituents inferred from seattle.hcs
Starting time: 2025-08-31 22:59 UTC
Time step: 60.00 min  Length: 31.00 days
Mean water level: 1.84 m

Predictions generated: Thu Jul 24 19:29:53 2025 (System)
Heights in meters above MLLW
Prediction date and time in Universal Time (UTC)
```
<img width="2600" height="1639" alt="pstide_selected_segment" src="https://github.com/user-attachments/assets/70311672-8b6e-42a4-bccd-a9597e347aa0" />

# Example 3. Gridded prediction of tides

Next we show how to predict the time series of tides in all of the segments, and interpolate the predicted tide series to a grid of the entire Puget Sound. The grid we are using is the subset of the [LiveOcean](https://faculty.washington.edu/pmacc/LO/LiveOcean.html) ROMS grid that contains the pstide segments. Using grid=True activates pstide to perform the gridded prediction of tides. This method produces a netcdf file (tides_gridded.nc) which contains the tides in every grid cell at every time step. An xarray dataset of the gridded predictions is added to the result dictionary. This method also produces the animated gif (tides_gridded.gif) of the predictions that is shown below.   
```
from pstide import run_pstide
result = run_pstide(grid=True, start='2024-08-01', interval=5, fps=10, length=1.0)
```
![pstide_gridded_predictions](https://github.com/user-attachments/assets/f6672e79-eaa0-4ff9-ac27-fa04e7713980)

# Example 4. Map the locations of model segments

Copy/paste and run the following in Jupyter Notebook to produce a map showing the locations of the model segments. The map will be saved in the working directory with the default name 'pstide_segments.png'. The dataframe of information about segment locations is saved when you use run_pstide in result['segment_locations']
```
from pstide import map_segments
map_segments()
```
<img width="2540" height="3417" alt="pstide_segments" src="https://github.com/user-attachments/assets/18150266-e308-4041-a071-291064f96759" />

# User instructions

Running help(run_pstide) in your notebook provides the following user instructions, including a list of the optional keyword arguments, and the contents of the output result dictionary:

```
Help on function run_pstide in module pstide:

run_pstide(**kwargs)
    Puget Sound Tide Channel Model for Python 3.x

    Adapted from the Python 2.x pstide module by David Finlayson

    Modified to run in Python 3.x by Greg Pelletier

    The Puget Sound Tide Channel Model (PSTCM) was first published in the late 1980's:

    Lavelle, J. W., H. O. Mofjeld, et al. (1988). A multiply-connected channel
      model of tides and tidal currents in Puget Sound, Washington and a comparison
      with updated observations. Seattle, WA, Pacific Marine Environmental
      Laboratory: 103pp. NOAA Technical Memorandum ERL PMEL-84

    Keyword arguments (any/all are optional)
        'segment': Optional segment number between 1 and 589 (default None)
        'lon': Optional longitude to use the nearest segment (default None)
        'lat': Optional latitude to use the nearest segment (default None)
        'start': Start datetime as ISO (e.g. '2025-08-01T00:00:00') (default now),
        'length': Length of predicted tide time series days (default 7.0),
        'interval': Time interval of tide time series minutes (default 60),
        'pacific': Use Pacific time zone instead of UTC (default True),
        'verbose': Print the selected segment info on screen (default True)
        'show_plot': Make a plot of the tide height time series (default True)
        'title': Inlcude title and header info in output text file (default True),
        'outfile': Output filename for selected segment for tide in meters and feet MMLW
            (default 'pstide_selected_segment.csv'),
        'outfile_all': Output filename for all segments for tide in meters MLLW
            (default 'pstide_all_segments.csv'),
        'plotfile': Plot filename for tide at selected segment in selected units
            (default 'pstide_selected_segment.png'),
        'julian': Use Julian date format for outpout (default False),
        'feet': Use feet instead of meters for units of tide height (default False),
        'grid': Interpolate gridded pstide predictions to subgrid of LiveOcean
            ROMS grid (default False),
        'frames_dir': Name of folder to store animiation frames of gridded predictions
            (default 'frames'),
        'fps': Frame rate of animated gif of gridded predictions (default 10 fps),
        'dpi': Resolution of the animated gif of gridded predictions (default 100 dpi),
        'cmap': Colormap for animated gif of gridded predictions (Default 'viridis_r')
        'show_gif': Display the animiated gif of gridded predictions on screen
            (default False),
        'gifname': File name for animated gif of gridded predictions
            (default 'pstide_gridded_predictions.gif'),
        'ncfile': File name for netcdf of gridded predictions
            (default 'pstide_gridded_predictions.nc')

    Returns.
        dictionary of all results including the following:
            options: input options specified in kwargs
            segdata: segment data for the harmonic constituents of the selected segment
            harmonic_constants: dictionary of harmonic constituents for all segments
            segment_locations: dataframe of segment locations data for all segments
            tides_all: dataframe of tide predictions for the all segments (meters MLLW)
            tides_selected: dataframe of tide predictions for the selected segment
            tides_gridded: xarray dataset of tide predictions interpolated
                to LiveOcean ROMS subgrid
```

# Detailed maps of segment locations

![north_sound](https://github.com/user-attachments/assets/2f210d59-b13a-4a7e-b732-869e4bbbf525)

![main_basin](https://github.com/user-attachments/assets/11f5e8d4-2dbc-4313-9ae1-bc27d8a0dbc1)

![hood_canal](https://github.com/user-attachments/assets/1f00b512-aecf-4d54-9af1-b001aff8dd77)

![south_sound_east](https://github.com/user-attachments/assets/0cc0b15f-57f6-4133-822b-c3f4addb1f7a)

![south_sound_west](https://github.com/user-attachments/assets/a5732981-9781-4377-bcc7-5e1eef033159)

