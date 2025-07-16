# -*- coding: utf-8 -*-

__version__ = "2.1.14"

#----------------------------------------------------------------------------
#  ps_tide.py - Tide prediction Software for Puget Sound                    
#                                                                           
#  Adapted from the original version 1.1.1 for Python 2.x by
#  David Finlayson                                                          
#  Nov 08, 2004                                                             
#  Version 1.1.1      
#                                                      
#  Updated to Python 3.x by 
#  Greg Pelletier
#  Jul 15 2025
#     
#----------------------------------------------------------------------------

#  WARNING: this code is only to be used for research purposes; not
#  for navigation.The official tidal predictions of the United States
#  are available from NOAA/NOS (www.co-ops.nos.noaa.gov)

#  References
#  ----------
#
#  Lavelle, J. W., H. O. Mofjeld, et al. (1988). A multiply-connected
#  channel model of tides and tidal currents in Puget Sound,
#  Washington and a comparison with updated observations. Seattle, WA,
#  Pacific Marine Environmental Laboratory: 103.
#
#  Mofjeld, H. O. and L. H. Larsen (1984). Tides and tidal currents of
#  the inland waters of western Washington. Seattle, Washington,
#  Pacific Marine Environmental Laboratory: 51.

import sys
import os
import pickle
from argparse import ArgumentParser
from time import ctime
# from calendar import jd_to_cal, cal_to_jd, jd_to_ISO, lt_to_ut, ut_to_lt, now, hms_to_fday, fday_to_hms
# from tidefun import predict_tides

# ----------------------------- Date Conversion -----------------------------
def string_to_date(datetext):
    date, time = datetext[:17].split()
    year, month, day = [int(x) for x in date.split('-')]
    hour, minute = [int(x) for x in time.split(':')]
    return year, month, day, hour, minute, 0

def is_valid_date(datetext):
    try:
        string_to_date(datetext)
        return True
    except Exception:
        return False

# ----------------------------- Title Printing -----------------------------
def print_title(fout, segment, segdata, datetext, options):
    from time import ctime
    name = segdata['name']
    refstation = segdata['refstation']
    lon, lat = segdata['longitude'], segdata['latitude']
    mean = segdata['hcs']['mean']
    tzname = "Local" if options['pacific'] else "JD" if options['julian'] else "UTC"
    delim = options['delimiter']

    fout.write(f"Puget Sound Tide Model: Tide Predictions\n")
    fout.write(f"Segment Index: {segment} ({name})\n")
    fout.write(f"Longitude: {lon:.6f}  Latitude: {lat:.6f}\n")
    fout.write(f"Minor constituents inferred from {refstation}\n")
    fout.write(f"Starting time: {datetext}\n")
    fout.write(f"Time step: {options['interval']:.2f} min  Length: {options['length']:.2f} days\n")
    fout.write(f"Mean water level: {mean * (3.2808 if options['feet'] else 1):.2f} {'ft' if options['feet'] else 'm'}\n\n")
    fout.write(f"Predictions generated: {ctime()} (System)\n")
    fout.write(f"Heights in {'feet' if options['feet'] else 'meters'} above MLLW\n")

    if tzname == "UTC":
        fout.write(f"Prediction date and time in Universal Time (UTC)\n")
        fout.write(f"\nDatetime{delim}Height\n")
    elif tzname == "Local":
        fout.write(f"Prediction date and time in Pacific Time (PST or PDT)\n")
        fout.write(f"\nDatetime{delim}Height\n")
    else:
        fout.write("Prediction date and time in Julian Days (JD)\n")
        fout.write(f"\nDay{delim}Height\n")

    if options['verbose']:

        print(f"Puget Sound Tide Model: Tide Predictions\n")
        print(f"Segment Index: {segment} ({name})")
        print(f"Longitude: {lon:.6f}  Latitude: {lat:.6f}")
        print(f"Minor constituents inferred from {refstation}")
        print(f"Starting time: {datetext}")
        print(f"Time step: {options['interval']:.2f} min  Length: {options['length']:.2f} days")
        print(f"Mean water level: {mean * (3.2808 if options['feet'] else 1):.2f} {'ft' if options['feet'] else 'm'}\n")
        print(f"Predictions generated: {ctime()} (System)")
        print(f"Heights in {'feet' if options['feet'] else 'meters'} above MLLW")
    
        if tzname == "UTC":
            print(f"Prediction date and time in Universal Time (UTC)\n")
            # print(f"\nDatetime{delim}Height\n")
        elif tzname == "Local":
            print(f"Prediction date and time in Pacific Time (PST or PDT)\n")
            # print(f"\nDatetime{delim}Height\n")
        else:
            print("Prediction date and time in Julian Days (JD)\n")
            # print(f"\nDay{delim}Height\n")
# ----------------------------- Tide Printing -----------------------------
def print_tide(fout, tide, options, df):
    '''
    append row of tide predictions to output file and df
    '''
    from pstide import ut_to_lt, jd_to_ISO, jd_to_cal, fday_to_hms
    jd = tide[0]
    height = tide[1]
    delim = options['delimiter']
    height_str = f"{height * (3.2808 if options['feet'] else 1):.1f}" if options['feet'] else f"{height:.2f}"

    if options['pacific']:
        jd_local, zone = ut_to_lt(jd)
        datetext = jd_to_ISO(jd_local, zone, "minute")
    elif options['julian']:
        datetext = f"{jd:12.4f}"
    else:
        year, month, fday = jd_to_cal(jd)
        hour, minute, _ = fday_to_hms(fday)
        datetext = f"{year:04d}-{month:02d}-{int(fday):02d} {hour:02d}:{minute:02d} UTC"

    # append row to output file
    fout.write(f"{datetext}{delim}{height_str}\n")

    # append row to df
    df.loc[len(df)] = [datetext, height_str]

def run_pstide(**kwargs):
    '''
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
        'title': Inlcude title and header info in output file (default True), 
        'outfile': Name of output file to save (default 'pstide_output.csv'), 
        'delimiter': Delimiter to use for output file (default ','), 
        'julian': Use Julian date format for outpout (default False),
        'feet': Use feet instead of meters for units of tide height (default False),
        'verbose': Print the predicted tides on screen (default True)

    Returns.
        df: Pandas dataframe of tide predictions
        
    '''
    
    import sys
    import os
    import pickle
    from pstide import cal_to_jd, hms_to_fday, lt_to_ut, predict_tides
    from argparse import ArgumentParser
    from datetime import datetime
    import pandas as pd
    
    # Define default values of input data arguments
    defaults = {
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
    
    # Update input options arguments with any provided keyword arguments in kwargs
    options = {**defaults, **kwargs}
    
    # print a warning for unexpected input kwargs
    unexpected = kwargs.keys() - defaults.keys()
    if unexpected:
        # raise ValueError(f"Unexpected argument(s): {unexpected}")
        print(f"Unexpected input kwargs: {unexpected}")

    # check for ps_segments.dat and load it into data dictionary
    file_name = "ps_segments.dat"
    ctrl = os.path.exists(file_name)
    if not ctrl:
        cwd = os.getcwd()
        print(f'Download {file_name} from https://github.com/gjpelletier/pstide and copy to your working directory {cwd}','\n')
        sys.exit()
    with open(file_name, 'rb') as fin:
        data = pickle.load(fin)

    # initialize output file
    try:
        fout = open(options['outfile'], 'w', encoding='utf-8') if options['outfile'] else sys.stdout
    except IOError:
        cwd = os.getcwd()
        print(f'Unable to write output file {options['outfile']} in your working directory {cwd}')
        sys.exit(1)

    # Parse the ISO string into a datetime object
    iso_string = options['start']
    dt = datetime.fromisoformat(iso_string)
    year = dt.year
    month = dt.month
    day = dt.day
    hour = dt.hour
    minute = dt.minute
    second = 0

    jd = cal_to_jd(year, month, day + hms_to_fday(hour, minute, second))
    jd_utc = lt_to_ut(jd) if options['pacific'] else jd

    segdata = data[options['segment']]

    tideseries = predict_tides(segdata['hcs'], jd_utc, options['interval'], options['length'])

    # Print results to the output stream
    if options['title'] == True:
        print_title(fout, options['segment'], segdata, options['start'], options)
       
    df = pd.DataFrame(columns=['Datetime', 'Height'])
    # df.style.set_properties(**{'text-align': 'left'})
    for tide in tideseries:
        print_tide(fout, tide, options, df)

    if options['verbose']:
        print(df.to_string(index=False))
    
    # if fout is not sys.stdout:
    #     fout.close()
    fout.close()
    
    result = {
        'options': options,
        'data': data,
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'second': second,
        'jd': jd,
        'jd_utc': jd_utc,
        'segdata': segdata,
        'tideseries': tideseries
    }
    
    return df

'''
# ----------------------------- Main Execution -----------------------------
def main():
    args = parse_arguments()

    if not os.path.exists('ps_segments.dat'):
        print_error('segment_data')
        sys.exit(1)

    with open('ps_segments.dat', 'rb') as fin:
        data = pickle.load(fin)

    if args.segment not in data:
        print_error('segment', args.segment)
        sys.exit(1)

    datetext = jd_to_ISO(int(now()) - 0.5, zone="UTC", level="minute") if args.start == 'today' else args.start
    if not is_valid_date(datetext):
        print_error('date', datetext)
        sys.exit(1)

    try:
        fout = get_output_stream(args.outfile)
    except IOError:
        print_error('file', args.outfile)
        sys.exit(1)

    year, month, day, hour, minute, second = string_to_date(datetext)
    jd = cal_to_jd(year, month, day + hms_to_fday(hour, minute, second))
    jd_utc = lt_to_ut(jd) if args.pacific else jd
    segdata = data[args.segment]
    tides = predict_tides(segdata['hcs'], jd_utc, args.interval, args.length)

    if args.title:
        print_title(fout, args.segment, segdata, datetext, args)

    for tide_entry in tides:
        print_tide_entry(fout, tide_entry, args)

    if fout is not sys.stdout:
        fout.close()

if __name__ == "__main__":
    main()
'''    
    
#------------------------------------------------------------------------------
# calendar.py - A library of calendar functions
#
# Copyright 2000, 2001 William McClain
# Modified by David Finlayson (no longer depends on exogenous files)
#
# Reference: Jean Meeus, _Astronomical Algorithms_, second edition,
# 1998, Willmann-Bell, Inc.
#------------------------------------------------------------------------------ 
# from math import *
# from time import gmtime

# Calendar Constants (modify for your purposes)
standard_timezone_name = 'PST'
standard_timezone_offset = 8.0/24.0
daylight_timezone_name = 'PDT'
daylight_timezone_offset = 7.0/24.0
month_names = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
minutes_per_day = 60.0 * 24.0
seconds_per_day = minutes_per_day * 60.0

class Error(Exception):
    """local exception class"""
    pass

def cal_to_jd(yr, mo = 1, day = 1, gregorian = True):
    """Convert a date in the Julian or Gregorian calendars to the Julian Day Number (Meeus 7.1).
    
    Parameters:
        yr        : year
        mo        : month (default: 1)
        day       : day, may be fractional day (default: 1)
        gregorian : If True, use Gregorian calendar, else use Julian calendar (default: True)
        
    Return:
        jd        : julian day number
    
    """
    if mo <= 2:
        yr = yr - 1
        mo = mo + 12
    if gregorian:
        A = int(yr / 100)
        B = 2 - A + (A / 4)
    else:
        B = 0
    return int(365.25 * (yr + 4716)) + int(30.6001 * (mo + 1)) + day + B - 1524.5


def cal_to_day_of_year(yr, mo, dy, gregorian = True):
    """Convert a date in the Julian or Gregorian calendars to day of the year (Meeus 7.1).
    
    Parameters:
        yr        : year
        mo        : month 
        day       : day 
        gregorian : If True, use Gregorian calendar, else use Julian calendar (default: True)
        
    Return:
        day number : 1 = Jan 1...365 (or 366 for leap years) = Dec 31.

    """
    if is_leap_year(yr, gregorian): 
        K = 1
    else: 
        K = 2
    dy = int(dy)
    return int(275 * mo / 9.0) - (K * int((mo + 9) / 12.0)) + dy - 30


def day_of_year_to_cal(yr, N, gregorian = True):
    """Convert a day of year number to a month and day in the Julian or Gregorian calendars.
    
    Parameters:
        yr        : year
        N         : day of year, 1..365 (or 366 for leap years) 
        gregorian : If True, use Gregorian calendar, else use Julian calendar (default: True)
        
    Return:
        month
        day
    
    """
    if is_leap_year(yr, gregorian): 
        K = 1
    else: 
        K = 2
    if (N < 32):
        mo = 1
    else:
        mo = int(9 * (K+N) / 275.0 + 0.98)
    dy = int(N - int(275 * mo / 9.0) + K * int((mo + 9) / 12.0) + 30)
    return mo, dy


def easter(yr, gregorian = True):
    """Return the date of Western ecclesiastical Easter for a year in the Julian or Gregorian calendars.
    
    Parameters:
        yr        : year
        gregorian : If True, use Gregorian calendar, else use Julian calendar (default: True)
        
    Return:
        month
        day    

    """
    yr = int(yr)
    if gregorian: 
        a = yr % 19
        b = yr / 100
        c = yr % 100
        d = b / 4
        e = b % 4
        f = (b + 8) / 25
        g = (b - f + 1) / 3
        h = (19 * a + b - d - g + 15) % 30
        i = c / 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) / 451
        tmp = h + l - 7 * m + 114
    else:
        a = yr % 4
        b = yr % 7
        c = yr % 19
        d = (19 * c + 15) % 30
        e = (2 * a + 4 * b - d + 34) % 7
        tmp = d + e + 114
    mo = tmp / 31
    dy = (tmp % 31) + 1
    return mo, dy

def fday_to_hms(days):
    """Convert fractional day (0.0..1.0) to integral hours, minutes, seconds.

    Parameters:
        day : a fractional day in the range 0.0..1.0
        
    Returns:
        hour : 0..23
        minute : 0..59
        seccond : 0..59
    
    """
    import math
    dfrac = days % 1
    (hfrac, hours) = math.modf(dfrac * 24.0)
    (mfrac, minutes) = math.modf(hfrac * 60.0)
    seconds = mfrac * 60.0
    return((int(hours), int(minutes), seconds))

def hms_to_fday(hr, mn, sec):
    """Convert hours-minutes-seconds into a fractional day 0.0..1.0.
    
    Parameters:
        hr : hours, 0..23
        mn : minutes, 0..59
        sec : seconds, 0..59
        
    Returns:
        fractional day, 0.0..1.0
    
    """
    minutes_per_day = 60.0 * 24.0
    seconds_per_day = minutes_per_day * 60.0
    
    return ((hr  / 24.0) + (mn  / minutes_per_day) + (sec / seconds_per_day))

def is_dst(jd, st_offset=8.0/24.0, dt_offset=7.0/24.0):
    """Is this instant within the Daylight Savings Time period as used in the US?
    
    Parameters:
        jd : Julian Day number representing an instant in Universal Time
        
    Return:
        True if Daylight Savings Time is in effect, false otherwise.
           
    """

    #
    # What year is this?
    # 
    yr, mon, day = jd_to_cal(jd)
    
    #
    # First day in April
    # 
    start = cal_to_jd(yr, 4, 1)
    
    #
    # Advance to the first Sunday
    #
    dow = jd_to_day_of_week(start)
    if dow:
        start = start + (7 - dow)

    #
    # Advance to 2AM
    #         
    start = start + 2.0 / 24
    
    #
    # Convert to Universal Time
    #
    start = start + st_offset

    if jd < start:
        return False
        
    #
    # Last day in October
    #
    stop = cal_to_jd(yr, 10, 31)
    
    #
    # Backup to the last Sunday
    # 
    dow = jd_to_day_of_week(stop)
    stop = stop - dow

    #
    # Advance to 2AM
    #         
    stop = stop + 2.0 / 24
    
    #
    # Convert to Universal Time
    #
    stop = stop + dt_offset
    
    if jd < stop:
        return True
        
    return False
        

def is_leap_year(yr, gregorian = True):
    """Return True if this is a leap year in the Julian or Gregorian calendars
    
    Parameters:
        yr        : year
        gregorian : If True, use Gregorian calendar, else use Julian calendar (default: True)
        
    Return:
        True is this is a leap year, else false.
        
    """
    yr = int(yr)
    if gregorian:
        return (yr % 4 == 0) and ((yr % 100 != 0) or (yr % 400 == 0))
    else:    
        return yr % 4 == 0
        

def jd_to_cal(jd, gregorian = True):
    """Convert a Julian day number to a date in the Julian or Gregorian calendars.
    
    Parameters:
        jd        : Julian Day number
        gregorian : If True, use Gregorian calendar, else use Julian calendar (default: True)
        
    Return:
        year
        month
        day (may be fractional)

    Return a tuple (year, month, day). 
    
    """
    import math
    
    jd = jd + 1e-9
    F, Z = math.modf(jd + 0.5)
    Z = int(Z)
    if gregorian:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - int(alpha / 4)
    else:
        A = Z
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E) + F
    if E < 14:
        mo = E - 1
    else:
        mo = E - 13
    if mo > 2:
        yr = C - 4716
    else:
        yr = C - 4715
    return yr, mo, day


def jd_to_day_of_week(jd):
    """Return the day of week for a Julian Day Number.
    
    The Julian Day Number must be for 0h UT.

    Parameters:
        jd : Julian Day number
        
    Return:
        day of week: 0 = Sunday...6 = Saturday.
    
    """
    i = jd + 1.5
    return int(i) % 7
    

def jd_to_jcent(jd):
    """Return the number of Julian centuries since J2000.0

    Parameters:
        jd : Julian Day number
        
    Return:
        Julian centuries
        
    """
    return (jd - 2451545.0) / 36525.0
    

def jd_to_ISO(jd, zone = "", level = "second"):
    """Convert time in Julian Days to an ISO formated string.
    
    The general format is:
    
        YYYY-MMM-DD HH:MM:SS ZZZ
    
    Truncate the time value to seconds, minutes, hours or days as
    indicated. If level = "day", don't print the time zone string.
    
    Pass an empty string ("", the default) for zone if you want to do 
    your own zone formatting in the calling module.
    
    Parameters:
        jd    : Julian Day number
        zone  : Time zone string (default = "")
        level : "day" or "hour" or "minute" or "second" (default = "second")
        
    Return:
        formatted date/time string
    
    """
    yr, mon, day = jd_to_cal(jd)
    hr, mn, sec = fday_to_hms(day)
    iday = int(day)

    month_names = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    month = month_names[mon-1]

    if level == "second":    
        return "%d-%s-%02d %02d:%02d:%02d %s" % (yr, month, iday, hr, mn, sec, zone)
    if level == "minute":    
        return "%d-%s-%02d %02d:%02d %s" % (yr, month, iday, hr, mn, zone)
    if level == "hour":    
        return "%d-%s-%02d %02d %s" % (yr, month, iday, hr, zone)
    if level == "day":    
        return "%d-%s-%02d" % (yr, month_names[mon-1], iday)
    # raise Error, "unknown time level = " + level

def lt_to_ut(jd, st_offset=8.0/24.0, dt_offset=7.0/24.0):
    """ converts a local time (JD) into UT. TimeZones are converted """
    if is_dst(jd, 0, 0):
        jd = jd + dt_offset
    else:
        jd = jd + st_offset
    return(jd)
    
def now():
    """Return the Julian Day at this instant"""
    from time import gmtime
    (year, month, day, hour, minute, second, wday, yday, isdst) = gmtime()
    day = day + hms_to_fday(hour, minute, second)
    jd = cal_to_jd(year, month, day)
    return(jd)
        

def sidereal_time_greenwich(jd):
    """Return the mean sidereal time at Greenwich.
    
    The Julian Day number must represent Universal Time.
    
    Parameters:
        jd : Julian Day number
        
    Return:
        sidereal time in radians (2pi radians = 24 hrs)
    
    """
    T = jd_to_jcent(jd)
    T2 = T * T
    T3 = T2 * T
    theta0 = 280.46061837 + 360.98564736629 * (jd - 2451545.0)  + 0.000387933 * T2 - T3 / 38710000
    theta0 = theta0 % 360
    result = radians(theta0)
    return(result)


def ut_to_lt(jd):
    """Convert universal time in Julian Days to a local time.
    
    Include Daylight Savings Time offset, if any.
        
    Parameters:
        jd : Julian Day number, universal time
        
    Return:
        Julian Day number, local time
        zone string of the zone used for the conversion

    """
    if is_dst(jd):
        zone = 'PDT'
        offset = 7.0/24.0
    else:
        zone = 'PST'
        offset = 8.0/24.0
        
    jd = jd - offset
    return jd, zone
    
if __name__ == '__main__':
    jd = cal_to_jd(2004, 10, 16)

    # Convert GMT to PDT    
    jd, zone = ut_to_lt(jd)
    (year, month, day) = jd_to_cal(jd)
    (hour, minute, second) = fday_to_hms(day)
    print(jd_to_ISO(jd, zone, "second"))

    # Convert PDT back to GMT
    jd = lt_to_ut(jd)
    (year, month, day) = jd_to_cal(jd)
    (hour, minute, second) = fday_to_hms(day)
    print(jd_to_ISO(jd, "UTC", "second"))
      
#----------------------------------------------------------------------------
#  tidefun.py - Tide prediction functions for Puget Sound                    
#                                                                           
#  David Finlayson                                                          
#  Jun 10, 2004                                                             
#  Version 1.1.1
# 
#----------------------------------------------------------------------------

#  These algorythms were ported from Fortran code given me by H. Mofjeld.
#  They represent the tidal portion of the Puget Sound Tide Channel Model.
#  See README.txt for more information

#  References
#  ----------
#
#  Lavelle, J. W., H. O. Mofjeld, et al. (1988). A multiply-connected
#  channel model of tides and tidal currents in Puget Sound,
#  Washington and a comparison with updated observations. Seattle, WA,
#  Pacific Marine Environmental Laboratory: 103.
#
#  Mofjeld, H. O. and L. H. Larsen (1984). Tides and tidal currents of
#  the inland waters of western Washington. Seattle, Washington,
#  Pacific Marine Environmental Laboratory: 51.
# from calendar import hms_to_fday, cal_to_jd
from math import cos, sin, tan, acos, asin, atan, sqrt

def predict_tides(hcs, jd, step_mins, series_days):
    " predict tides using 37 harmonic constituents "
    #--------------------------------------------------------------------
    #  Input:
    #  ------
    #    hcs         - harmonic dictionary*
    #    jd          - julian date (UTC)
    #    step_mins   - predicion interval in minutes (float)
    #    series_days - length of record in days (float)
    #
    #    * the hcs dictionary is built by the program compile_hcs.py
    #
    #  Output:
    #  -------
    #    JD   - Julian Date (float)
    #    tide - tide elevation (meters)
    #
    #  The predictions begin at the specified starting date and time
    #  (UTC) and are made for a specified number of days (series_days)
    #  at the specified interval (step_mins); they are returned in a
    #  two columns touple (julian day, tide level meters).
    #
    #  Modified from tides_2001.f by H. Mofjeld (2004 March 04)
    #  Modified from predict_tides.f by D. Finlayson (2004 May 22)
    #------------------------------------------------------------------
    
    #  Parameters
    NC = 37   # Number of Harmonic Constituents (Full Set)
    NH = 5    # Number of Harmonic Constituents (Model)

    rad = 0.017453292519943 # degrees to radians
    tnode = 30.5            # monthly interval to update lunar nodes
    jd2000 = 2451544.50     # julian day of the year 2000
    index = 0
    constit = ('SA','SSA','MM','MSF','MF','2Q1','Q1','RHO','O1','M1','P1','S1',
               'K1','J1','OO1','2N2','MU2','N2','NU2','M2','LAM2','L2','T2','S2',
               'R2','K2','2SM2','2MK3','M3','MK3','MN4','M4','MS4','S4','M6','S6',
               'M8')

    mean = hcs['mean']

    H = []  # Harmonic Amplitude (m)
    G = []  # Phase Lag (deg)
    for const in constit:
        H.append(hcs[const][0])
        G.append(hcs[const][1])

    #  Converting phase lags to radians
    for i in range(0, NC):
        G[i] = rad * G[i]

    # Tidal Predictions

    #  Initial time parameters
    JD0 = jd
    step_days = step_mins / (24.0 * 60.0)
    series_length = int(series_days / step_days)
    nodeint  = tnode / step_days

    #  Loop over time
    prediction = [None] * series_length
    for j in range(0, series_length):
        JD = JD0 + step_days * j

       # Nudge time a hair so that day fractions convert to times cleanly
        JD = JD + 1.0e-9 
        d2000 = JD - jd2000
        tide = mean

        #  Computing V0 phases, updated each time step
        V0 = v2000(d2000)

        #  Updating f-factors, u-phases every 30.5 days, centered in the
        #  middle of the 30.5-day interval

        # Python: first iteration is 0 not 1, so changed test to 0, not 1
        if(j % nodeint == 0):
            (f, u) = node2000(d2000 + 15.25)

        #  Loop over tidal constituents
        for i in range(0, NC):
            r=f[i]*H[i]
            phase=V0[i]+u[i]-G[i]
            tide=tide+r*cos(phase)

        #  Outputing prediction at time t
        prediction[j] = (JD, tide)
    return(prediction)

def v2000(d2000):
    "  Computing V0 phases Reference: Schureman, 1976 "
    NC = 37
    rad = 0.017453292519943
    V = [None] * NC
    V0 = [None] * NC

    dphase = 360.0 * (d2000 % 1.0)

    for i in range(0, 5):
        V0[i] = 0.0

    for i in range(5, 15):
        V0[i] = 1.0 * dphase

    for i in range(15, 27):
        V0[i] = 2.0 * dphase

    for i in range(27, 30):
        V0[i] = 3.0 * dphase

    for i in range(30, 34):
        V0[i] = 4.0 * dphase

    V0[34] = 6.0 * dphase
    V0[35] = 6.0 * dphase
    V0[36] = 8.0 * dphase

    T  = (d2000 + 36524.5)/36525
    s  = (270.437  + 481267.892 * T + 0.0025*T**2) % 360.0
    h  = (279.697  +  36000.769 * T + 0.0003*T**2) % 360.0
    p  = (334.328  +   4069.040 * T - 0.0103*T**2) % 360.0
    p1 = (281.221  +      1.719 * T + 0.0005*T**2) % 360.0

    V[0]  =    1.0 * h                                # SA
    V[1]  =    2.0 * h                                # SSA
    V[2]  =    1.0 * s + 0.0 * h - 1.0 * p            # MM
    V[3]  =    2.0 * s + 0.0 * h - 2.0 * p            # MSF
    V[4]  =    2.0 * s + 0.0 * h + 0.0 * p            # MF
    V[5]  =  - 4.0 * s + 1.0 * h + 2.0 * p - 90.0     # QQ
    V[6]  =  - 3.0 * s + 1.0 * h + 1.0 * p - 90.0     # Q1
    V[7]  =  - 3.0 * s + 3.0 * h - 1.0 * p - 90.0     # RHO
    V[8]  =  - 2.0 * s + 1.0 * h + 0.0 * p - 90.0     # O1
    V[9]  =  - 1.0 * s + 1.0 * h + 0.0 * p - 90.0     # M1
    V[10] =  - 0.0 * s - 1.0 * h + 0.0 * p - 90.0     # P1
    V[11] =    180.0                                  # S1
    V[12] =  - 0.0 * s + 1.0 * h + 0.0 * p + 90.0     # K1
    V[13] =    1.0 * s + 1.0 * h - 1.0 * p + 90.0     # J1
    V[14] =    2.0 * s + 1.0 * h + 0.0 * p + 90.0     # OO
    V[15] =  - 4.0 * s + 2.0 * h + 2.0 * p            # NN
    V[16] =  - 4.0 * s + 4.0 * h + 0.0 * p            # MU
    V[17] =  - 3.0 * s + 2.0 * h + 1.0 * p            # N2
    V[18] =  - 3.0 * s + 4.0 * h - 1.0 * p            # NU
    V[19] =  - 2.0 * s + 2.0 * h + 0.0 * p            # M2
    V[20] =  - 1.0 * s + 0.0 * h + 1.0 * p + 180.0    # LAM
    V[21] =  - 1.0 * s + 2.0 * h - 1.0 * p + 180.0    # L2
    V[22] =  - 0.0 * s - 1.0 * h + 1.0 * p1           # T2
    V[23] =    0.0                                    # S2
    V[24] =  - 0.0 * s + 1.0 * h - 1.0 * p1 + 180.0   # R2
    V[25] =  - 0.0 * s + 2.0 * h + 0.0 * p1           # K2
    V[26] =    2.0 * s - 2.0 * h + 0.0 * p            # 2MS2
    V[27] =  - 4.0 * s + 3.0 * h + 0.0 * p - 90.0     # 2MK3
    V[28] =  - 3.0 * s + 3.0 * h + 0.0 * p +180.0     # M3
    V[29] =  - 2.0 * s + 3.0 * h + 0.0 * p + 90.0     # MK3
    V[30] =  - 5.0 * s + 4.0 * h + 1.0 * p            # MN4
    V[31] =  - 4.0 * s + 4.0 * h + 0.0 * p            # M4
    V[32] =  - 2.0 * s + 2.0 * h + 0.0 * p            # MS4
    V[33] =    0.0                                    # S4
    V[34] =  - 6.0 * s + 6.0 * h + 0.0 * p            # M6
    V[35] =    0.0                                    # S6
    V[36] =  - 8.0 * s + 8.0 * h + 0.0 * p            # M8

    for i in range(0, NC):
        V0[i] = rad * (V0[i] + V[i])
    return(V0)

def node2000(d2000):
    "  Computing node factors f and phases u Ref.: Schureman Tables "
    rad = 0.017453292519943
    NC = 37

    T   = ( d2000 + 36524.5 )/36525.0
    N   = (259.183 - 1934.142 * T + 0.0021 * T * T) % 360.0
    if(N < 0.0): N = N + 360.0

    N = rad*N
    p  = (334.328 + 4069.040 * T - 0.0103*T**2) % 360.0
    p = rad * p

    I   = acos(0.9136949 - 0.035696 * cos(N))
    nu  = asin(0.0897056 * sin(N)/sin(I))
    eta = atan(cos(I) * tan(nu))
    nup = atan((sin(nu) * sin(2.0 * I))/(cos(nu)*sin(2.0*I) + 0.3347))
    nupp2 = atan((sin(2.0*nu) * sin(I)**2)/(cos(2.0*nu)*sin(I)**2 + 0.0727))
    PP = p - eta

    f = [None] * NC
    f[0] = 1.000                                                        # SA
    f[1] = 1.000                                                        # SSA
    f[2] = (2.0/3.0-sin(I)**2)/0.5021                                   # MM
    f[3] = cos(I/2.0)**4/0.9154                                         # MSF
    f[4] = sin(I)**2/0.1578                                             # MF
    f[5] = sin(I)*cos(I/2.0)**2/0.37988                                 # QQ
    f[6] = sin(I)*cos(I/2.0)**2/0.37988                                 # Q1
    f[7] = sin(I)*cos(I/2.0)**2/0.37988                                 # RHO1
    f[8] = sin(I)*cos(I/2.0)**2/0.37988                                 # O1
    Qai = sqrt(0.25 + 1.5 * cos(I) * cos(2.0 * PP)/cos(I/2.0)**2 + \
               2.25 * cos(I)**2/cos(I/2.0)**4)
    f[9] = f[8] * Qai                                                   # M1
    f[10] = 1.000                                                       # P1
    f[11] = 1.000                                                       # S1
    f[12] = sqrt(0.8965 * sin(2.0 * I)**2 + 0.6001 * sin(2.0 * I) * \
                 cos(nu) + 0.1006)                                      # K1
    f[13] = sin(2.0 * I)/0.72137                                        # J1
    f[14] = sin(I)*sin(I/2.0)**2/0.016358                               # OO
    f[15] = cos(I/2.0)**4/0.9154                                        # NN
    f[16] = cos(I/2.0)**4/0.9154                                        # MU2
    f[17] = cos(I/2.0)**4/0.9154                                        # N2
    f[18] = cos(I/2.0)**4/0.9154                                        # NU2
    f[19] = cos(I/2.0)**4/0.9154                                        # M2
    f[20] = cos(I/2.0)**4/0.9154                                        # LAM
    Rai = sqrt(1.0 - 12.0*tan(I/2.0)**2 * cos(2.0*PP) + 36.0 * \
               tan(I/2.0)**4)
    f[21] = f[19] * Rai                                                 # L2
    f[22] = 1.000                                                       # T2
    f[23] = 1.000                                                       # S2
    f[24] = 1.000                                                       # R2
    f[25] = sqrt( 19.0444*sin(I)**4 + 2.7702*cos(2.0*nu)* \
                  sin(I)**2 + 0.0981)                                   # K2
    f[26] = cos(I/2.0)**4/0.9154                                        # 2SM2
    f[27] = f[19]**2*f[12]                                              # 2MK3
    f[28] = cos(I/2.0)**6/0.8758                                        # M3
    f[29] = f[19]*f[12]                                                 # MK3
    f[30] = f[19]**2                                                    # MN4
    f[31] = f[19]**2                                                    # M4
    f[32] = f[19]**2                                                    # MS4
    f[33] = 1.000                                                       # S4
    f[34] = f[19]**3                                                    # M6
    f[35] = 1.000                                                       # S6
    f[36] = f[19]**4                                                    # M8

    u = [None] * NC
    u[0] =  0.0                     # SA
    u[1] =  0.0                     # SSA
    u[2] =  0.0                     # MM
    u[3] =  0.0                     # MSF
    u[4] = -2.0*eta                 # MF
    u[5] =  2.0*eta - nu            # QQ
    u[6] =  2.0*eta - nu            # Q1
    u[7] =  2.0*eta - nu            # RHO
    u[8] =  2.0*eta - nu            # O1
    Q = atan( 0.483*tan(PP))
    u[9] =  1.0*eta - nu + Q        # M1
    u[10] = 0.0                     # P1
    u[11] = 0.0                     # S1
    u[12] = -nup                    # K1
    u[13] = -nu                     # J1
    u[14] = -2.0*eta - nu           # OO
    u[15] =  2.0*eta - 2.0*nu       # NN
    u[16] =  2.0*eta - 2.0*nu       # MU2
    u[17] =  2.0*eta - 2.0*nu       # N2
    u[18] =  2.0*eta - 2.0*nu       # NU2
    u[19] =  2.0*eta - 2.0*nu       # M2
    u[20] =  2.0*eta - 2.0*nu       # LAM
    R = atan( sin(2.0*PP)/( 1.0/( 6.0*tan(I/2.0)**2 ) - cos(2.0*PP) ) )
    u[21] =  2.0*eta - 2.0*nu - R   # L2
    u[22] =  0.0                    # T2
    u[23] =  0.0                    # S2
    u[24] =  0.0                    # R2
    u[25] = -nupp2                  # K2
    u[26] = -2.0*eta + 2.0*nu       # 2SM2
    u[27] = 4.0*eta - 4.0*nu + nup  # 2MK3
    u[28] = 3.0*eta - 3.0*nu        # M3
    u[29] = 2.0*eta - 2.0*nu - nup  # MK3
    u[30] = 4.0*eta - 4.0*nu        # MN4
    u[31] = 4.0*eta - 4.0*nu        # M4
    u[32] = 2.0*eta - 2.0*nu        # MS4
    u[33] = 0.0                     # S4
    u[34] = 6.0*eta - 6.0*nu        # M6
    u[35] = 0.0                     # S6
    u[36] = 8.0*eta - 8.0*nu        # M8
    return(f, u)


      