# Puget Sound Tide Channel Model for Python 3.x

Adapted from the Python 2.x pstide module by David Finlayson

Modified to run in Python 3.x by Greg Pelletier

The Puget Sound Tide Channel Model (PSTCM) was first published in the late 1980's:

[Lavelle, J. W., H. O. Mofjeld, et al. (1988)](https://github.com/gjpelletier/pstide/blob/main/Lavelle_et_al_1988.pdf). A multiply-connected channel
  model of tides and tidal currents in Puget Sound, Washington and a comparison
  with updated observations. Seattle, WA, Pacific Marine Environmental
  Laboratory: 103pp. NOAA Technical Memorandum ERL PMEL-84

David Finlayson translated the Lavelle and Mofjeld's Fortran code to Python 2.x in 2004, and included the following paragraphs in a readme file:

<blockquote>
Hal Mofjeld (Oceanographer, PMEL) maintained the code and updated
it as languages and hardware have progressed; occasionally helping researchers
to accurate tide predictions in the Sound in water bodies where the official
NOAA predictions are unavailable or too distant to be accurate. (NOAA only
predicts tides at three primary stations in the Sound and publishes offsets for
other locations.)

In the late 1990's the increasing use of GIS in mapping lead to
attempts to merge bathymetry and topographic digital elevation models. Because
topography is referenced to NGVD29 or NAVD88 and bathymetry is referenced to
MLLW, it became obvious that an accurate tide model for Puget Sound was needed to model
the vertical datum differences. Hal dusted off the old Fortran code and
refactored it to handle the full suite of constituents used to make official
NOAA predictions (37 in all). It was as a GIS analyst that David Finlayson became aware of
the model. See Mofjeld et al. (2002) for details:

Mofjeld, H. O., A. J. Venturato, et al. (2002). Tidal datum distributions in
  Puget Sound, Washington, based on a tide model. Seattle, WA, NOAA/Pacific
  Marine Environmental Laboratory: 39.
</blockquote>

# Installing pstide

If you have not already installed pstide in your Python environment, enter the following with pip or !pip in your notebook or terminal:<br>
```
pip install git+https://github.com/gjpelletier/pstide.git
```

if you are upgrading from a previous installation, enter the following:<br>
```
pip install git+https://github.com/gjpelletier/pstide.git --upgrade
```

# Before first use of pstide

Before using pstide for the first time, you must download the [ps_segments.dat](https://github.com/gjpelletier/pstide/blob/main/ps_segments.dat) file from the following link and copy it into your working directory:

https://github.com/gjpelletier/pstide/blob/main/ps_segments.dat

# Example use of pstide

This example assumes you have already followed the instructions above for installing pstide and copying the ps_segments.dat file to your working directory.

Copy and run the following code in your Jupyter Notebook:
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

The code above returns the following output on screen and in the output pstide_output.csv and pstide_output.png:

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
<img width="2624" height="1654" alt="pstide_output" src="https://github.com/user-attachments/assets/0d35e0d9-4b68-44bc-8bb1-f806c8baa1bd" />

# Maps of Puget Sound and segment numbers

<img width="659" height="851" alt="Fig1_Map_of_Puget_Sound" src="https://github.com/user-attachments/assets/ff6f9d4d-5d91-4cdb-a951-9b0dbe4e6df3" />

![north_sound](https://github.com/user-attachments/assets/2f210d59-b13a-4a7e-b732-869e4bbbf525)

![main_basin](https://github.com/user-attachments/assets/11f5e8d4-2dbc-4313-9ae1-bc27d8a0dbc1)

![hood_canal](https://github.com/user-attachments/assets/1f00b512-aecf-4d54-9af1-b001aff8dd77)

![south_sound_east](https://github.com/user-attachments/assets/0cc0b15f-57f6-4133-822b-c3f4addb1f7a)

![south_sound_west](https://github.com/user-attachments/assets/a5732981-9781-4377-bcc7-5e1eef033159)

