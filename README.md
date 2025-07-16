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


If you have not already installed pstide, enter the following with pip or !pip in your notebook or terminal:<br>
```
pip install git+https://github.com/gjpelletier/pstide.git
```

if you are upgrading from a previous installation of PyMLR, enter the following with pip pr !pip in your notebook or terminal:<br>
```
pip install git+https://github.com/gjpelletier/pstide.git --upgrade
```

# Example

```
# Example use of run_pstide
from pstide import run_pstide
from datetime import datetime

kwargs = {
    'segment': '497', 
    'start': datetime.now().isoformat(), 
    'length': 1.0,
    'interval': 60,
    'pacific': True,
    'title': True, 
    'outfile': 'pstide_output.csv', 
    'delimiter': ',', 
    'julian': False,
    'feet': False,
    'verbose': True
    }
    
tides = run_pstide(**kwargs)
```
"""
             Datetime Height
2025-Jul-15 17:25 PDT   1.31
2025-Jul-15 18:25 PDT   2.10
2025-Jul-15 19:25 PDT   2.84
2025-Jul-15 20:25 PDT   3.40
2025-Jul-15 21:25 PDT   3.64
2025-Jul-15 22:25 PDT   3.56
2025-Jul-15 23:25 PDT   3.17
2025-Jul-16 00:25 PDT   2.61
2025-Jul-16 01:25 PDT   2.00
2025-Jul-16 02:25 PDT   1.49
2025-Jul-16 03:25 PDT   1.21
2025-Jul-16 04:25 PDT   1.19
2025-Jul-16 05:25 PDT   1.41
2025-Jul-16 06:25 PDT   1.80
2025-Jul-16 07:25 PDT   2.22
2025-Jul-16 08:25 PDT   2.54
2025-Jul-16 09:25 PDT   2.65
2025-Jul-16 10:25 PDT   2.52
2025-Jul-16 11:25 PDT   2.16
2025-Jul-16 12:25 PDT   1.65
2025-Jul-16 13:25 PDT   1.14
2025-Jul-16 14:25 PDT   0.75
2025-Jul-16 15:25 PDT   0.60
2025-Jul-16 16:25 PDT   0.75
"""


# Map of Puget Sound

<img width="659" height="851" alt="Fig1_Map_of_Puget_Sound" src="https://github.com/user-attachments/assets/ff6f9d4d-5d91-4cdb-a951-9b0dbe4e6df3" />

# Segment Numbers

![north_sound](https://github.com/user-attachments/assets/2f210d59-b13a-4a7e-b732-869e4bbbf525)

![main_basin](https://github.com/user-attachments/assets/11f5e8d4-2dbc-4313-9ae1-bc27d8a0dbc1)

![hood_canal](https://github.com/user-attachments/assets/1f00b512-aecf-4d54-9af1-b001aff8dd77)

![south_sound_east](https://github.com/user-attachments/assets/0cc0b15f-57f6-4133-822b-c3f4addb1f7a)

![south_sound_west](https://github.com/user-attachments/assets/a5732981-9781-4377-bcc7-5e1eef033159)

