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

# Example 1. Tides in Budd Inlet for the next 28 days

Copy/paste and run the following in Jupyter Notebook to produce the figure below showing the next 28 days of tides in Budd Inlet segment 44. This example shows how to specify the segment number, the time period (length) of the tide predictions, and how to use pacific=False to use datetimes in UTC. The defualt starting datetime is the current time. The tide predictions are also stored in the result dictionary as a pandas dataframe in result['df_tide'].
```
from pstide import run_pstide
result = run_pstide(segment=44, length=28, pacific=False)
```
<img width="2552" height="1639" alt="pstide_output" src="https://github.com/user-attachments/assets/4772da93-b01d-4081-baaf-61c417539a85" />

# Example 2. Tides at a specified longitide and latitude

Copy/paste and run the following in Jupyter Notebook to produce the figure below showing the tides closest to lon=-122.615 and lat=47.885 in August 2025. This example shows how to specify the longitude (lon), latitude (lat), starting datetime in ISO format, and the time period (length) of the tide predictions. The tide predictions are also stored in the result dictionary as a pandas dataframe in result['df_tide'].
```
from pstide import run_pstide
result = run_pstide(lon=-122.615, lat=47.885, start='2025-08-01T00:00:00', length=31)
```
<img width="2600" height="1639" alt="pstide_output" src="https://github.com/user-attachments/assets/d6d5df74-10ee-4f6a-a649-faa82c709d0b" />

# Example 3. Map the locations of model segments

Copy/paste and run the following in Jupyter Notebook to produce a map showing the locations of the model segments. The map will be saved in the working directory with the default name 'pstide_segments.png'.
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
        'segment': Optional segment number between 1 and 589 (default 497)
        'lon': Optional longitude to use the nearest segment (default None)
        'lat': Optional latitude to use the nearest segment (default None)
        'start': Start datetime as ISO (e.g. '2025-08-01T00:00:00') (default now),
        'length': Length of tide time series days (default 1.0),
        'interval': Time interval of tide time series minutes (default 60),
        'pacific': Use Pacific time zone instead of UTC (default True),
        'verbose': Print the predicted tides on screen (default False)
        'show_plot': Make a plot of the tide height time series (default True)
        'title': Inlcude title and header info in output text file (default True),
        'outfile': Name of output text file to save (default 'pstide_output.csv'),
        'plotfile': Name of output plot file to save (default 'pstide_output.png'),
        'delimiter': Delimiter to use for output file (default ','),
        'julian': Use Julian date format for outpout (default False),
        'feet': Use feet instead of meters for units of tide height (default False),

    Returns.
        dictionary of all results including the following:
            options: input options specified in kwargs
            segdata: segment data for the selected segment
            ps_segments: dictionary of ps_segments.dat for all segments
            segment_locations: dataframe of segment_locations.dat for all segments
            df_tide: dataframe of tide predictions for the selected segment
```

# Detailed maps of segment locations

![north_sound](https://github.com/user-attachments/assets/2f210d59-b13a-4a7e-b732-869e4bbbf525)

![main_basin](https://github.com/user-attachments/assets/11f5e8d4-2dbc-4313-9ae1-bc27d8a0dbc1)

![hood_canal](https://github.com/user-attachments/assets/1f00b512-aecf-4d54-9af1-b001aff8dd77)

![south_sound_east](https://github.com/user-attachments/assets/0cc0b15f-57f6-4133-822b-c3f4addb1f7a)

![south_sound_west](https://github.com/user-attachments/assets/a5732981-9781-4377-bcc7-5e1eef033159)

