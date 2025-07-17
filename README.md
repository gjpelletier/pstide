# Puget Sound Tide Channel Model for Python 3.x

Adapted from the pstide.py module for Python 2.x by David Finlayson

Modified to run in Python 3.x by Greg Pelletier

The Puget Sound Tide Channel Model was first published in the late 1980's:

[Lavelle, J. W., H. O. Mofjeld, et al. (1988)](https://github.com/gjpelletier/pstide/blob/main/Lavelle_et_al_1988.pdf). A multiply-connected channel
  model of tides and tidal currents in Puget Sound, Washington and a comparison
  with updated observations. Seattle, WA, Pacific Marine Environmental
  Laboratory: 103pp. NOAA Technical Memorandum ERL PMEL-84

# Warning

The pstide code is intended only to be used for research purposes; not for navigation. The official tidal predictions of the United States are available from NOAA/NOS (https://tidesandcurrents.noaa.gov/tide_predictions.html)

# Installing pstide

If you are installing for the first time, or upgrading from a previous installation, enter the following with pip or !pip in your notebook or terminal:<br>
```
pip install git+https://github.com/gjpelletier/pstide.git --upgrade
```

# Example 1. Tides for one day in Elliott Bay

Copy/paste and run the following code in your Jupyter Notebook:
```
from pstide import run_pstide

kwargs = {
    'segment': 497,                    # Puget Sound segment (1-589)
    'start': '2025-07-16T12:00:00',    # start datetime in ISO format
    'length': 1.0,                     # length of time to predict (days)
    'interval': 60,                    # time step of predictions (minutes)
    'pacific': True,                   # use Pacific time (PDT/PST)
    'verbose': True,                   # display results on screen
    'show_plot': True,                 # plot the results
    'outfile': 'pstide_output.csv',    # save results in csv
    'plotfile': 'pstide_output.png',   # save plot as png
    }
    
result = run_pstide(**kwargs)
```

Running the code above returns the following output on screen and in the 'result', 'pstide_output.csv', and 'pstide_output.png':

(note that the output 'result' above is a dictionary that includes the following keys: 'options': the kwargs input options, 'segdata': segment data for the selected segment, 'ps_segments': contents of ps_segments.dat, and 'df_tide': Pandas dataframe containing output of the tide predictions)

```
Puget Sound Tide Model: Tide Predictions

Segment Index: 497 (Elliott_Bay)
Longitude: -122.347915  Latitude: 47.591075
Minor constituents inferred from seattle.hcs
Starting time: 2025-07-16T12:00:00
Time step: 60.00 min  Length: 1.00 days
Mean water level: 2.02 m

Predictions generated: Wed Jul 16 13:10:13 2025 (System)
Heights in meters above MLLW
Prediction date and time in Pacific Time (PST or PDT)

                 Datetime  Height
2025-07-16 12:00:00-07:00   1.872
2025-07-16 13:00:00-07:00   1.346
2025-07-16 14:00:00-07:00   0.889
2025-07-16 15:00:00-07:00   0.631
2025-07-16 16:00:00-07:00   0.653
2025-07-16 17:00:00-07:00   0.972
2025-07-16 18:00:00-07:00   1.533
2025-07-16 19:00:00-07:00   2.220
2025-07-16 20:00:00-07:00   2.884
2025-07-16 21:00:00-07:00   3.379
2025-07-16 22:00:00-07:00   3.598
2025-07-16 23:00:00-07:00   3.493
2025-07-17 00:00:00-07:00   3.094
2025-07-17 01:00:00-07:00   2.494
2025-07-17 02:00:00-07:00   1.830
2025-07-17 03:00:00-07:00   1.249
2025-07-17 04:00:00-07:00   0.873
2025-07-17 05:00:00-07:00   0.769
2025-07-17 06:00:00-07:00   0.938
2025-07-17 07:00:00-07:00   1.314
2025-07-17 08:00:00-07:00   1.784
2025-07-17 09:00:00-07:00   2.218
2025-07-17 10:00:00-07:00   2.501
2025-07-17 11:00:00-07:00   2.565
```
<img width="2619" height="1639" alt="pstide_output" src="https://github.com/user-attachments/assets/681f70bc-53ca-4972-a56a-fd0a2ecaae86" />

# Example 2. Tides in Budd Inlet for the next 28 days

Copy/paste and run the following in Jupyter Notebook to produce the figure below showing the next 28 days of tides in Budd Inlet segment 44. The tide predictions are also stored in the result dictionary as a pandas dataframe in result['df_tide']. This example also shows how to get the output datetime values in UTC by using the argument pacific=False:
```
from pstide import run_pstide
result = run_pstide(segment=44, length=28, pacific=False)
```
<img width="2552" height="1639" alt="pstide_output" src="https://github.com/user-attachments/assets/4772da93-b01d-4081-baaf-61c417539a85" />

# Example 3. Tides at a specified longitide and latitude

Copy/paste and run the following in Jupyter Notebook to produce the figure below showing the tides closest to lon=-122.615 and lat=47.885 in August 2025. The tide predictions are also stored in the result dictionary as a pandas dataframe in result['df_tide'].
```
from pstide import run_pstide
result = run_pstide(lon=-122.615, lat=47.885, start= '2025-08-01T00:00:00', length=31)
```
<img width="2600" height="1639" alt="pstide_output" src="https://github.com/user-attachments/assets/d6d5df74-10ee-4f6a-a649-faa82c709d0b" />

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

    Args.
        'segment': Segment number as text '1' through '589' (default '497')
        'start': Starting datetime as ISO text string (default datetime.now().isoformat()),
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

# Maps of Puget Sound and segment numbers

<img width="659" height="851" alt="Fig1_Map_of_Puget_Sound" src="https://github.com/user-attachments/assets/ff6f9d4d-5d91-4cdb-a951-9b0dbe4e6df3" />

![north_sound](https://github.com/user-attachments/assets/2f210d59-b13a-4a7e-b732-869e4bbbf525)

![main_basin](https://github.com/user-attachments/assets/11f5e8d4-2dbc-4313-9ae1-bc27d8a0dbc1)

![hood_canal](https://github.com/user-attachments/assets/1f00b512-aecf-4d54-9af1-b001aff8dd77)

![south_sound_east](https://github.com/user-attachments/assets/0cc0b15f-57f6-4133-822b-c3f4addb1f7a)

![south_sound_west](https://github.com/user-attachments/assets/a5732981-9781-4377-bcc7-5e1eef033159)

