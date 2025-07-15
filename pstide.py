# -*- coding: utf-8 -*-

__version__ = "2.1.2"


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
#  With advice from Copilot
#  Jul 14 2025
#  Version 2.1.1      
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
# from calendar import jd_to_cal, cal_to_jd, jd_to_ISO, lt_to_ut, ut_to_lt, now, hms_to_fday, fday_to_hms
from pstide import jd_to_cal, cal_to_jd, jd_to_ISO, lt_to_ut, ut_to_lt, now, hms_to_fday, fday_to_hms
from time import ctime
from tidefun import predict_tides

# ----------------------------- Error Messaging -----------------------------
def print_error(message, value=None):
    errors = {
        'segment': f"Error: invalid segment '{value}'. Expected integer between 1 and 589.",
        'date': f"Error: invalid date string '{value}'. Use format 'YYYY-MM-DD HH:MM'.",
        'file': f"Error: cannot open output file: '{value}'.",
        'segment_data': "Error: missing model data file 'ps_segments.dat'. Run compile_hcs.py first."
    }
    print("\n" + errors.get(message, "Unknown error."))

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

# ----------------------------- Argument Parsing -----------------------------
def parse_arguments():
    parser = ArgumentParser(description="Puget Sound Tide Channel Model Predictor")
    parser.add_argument("segment", type=str, help="Segment index (1–589, some gaps)")
    parser.add_argument("-s", "--start", type=str, default="today", help="Start time: 'YYYY-MM-DD HH:MM' (default=today UTC)")
    parser.add_argument("-t", "--title", action="store_true", help="Include metadata title block")
    parser.add_argument("-o", "--outfile", type=str, default="", help="Output file (default=stdout)")
    parser.add_argument("-i", "--interval", type=float, default=60.0, help="Time step in minutes")
    parser.add_argument("-l", "--length", type=float, default=1.0, help="Series length in days")
    parser.add_argument("-d", "--delimiter", type=str, default="\t", help="Column delimiter (default='\\t')")
    parser.add_argument("-p", "--pacific", action="store_true", help="Use Pacific Time Zone")
    parser.add_argument("-j", "--julian", action="store_true", help="Output in Julian Days")
    parser.add_argument("-f", "--feet", action="store_true", help="Output tide heights in feet")

    args = parser.parse_args()
    return args

# ----------------------------- Output Handling -----------------------------
def get_output_stream(outfile):
    return open(outfile, 'w', encoding='utf-8') if outfile else sys.stdout

# ----------------------------- Title Printing -----------------------------
def print_title(fout, segment, segdata, datetext, options):
    name = segdata['name']
    refstation = segdata['refstation']
    lon, lat = segdata['longitude'], segdata['latitude']
    mean = segdata['hcs']['mean']
    tzname = "Local" if options.pacific else "JD" if options.julian else "UTC"
    delim = options.delimiter

    fout.write(f"Puget Sound Tide Model: Tides\n")
    fout.write(f"Segment Index: {segment} ({name})\n")
    fout.write(f"Longitude: {lon:.6f}  Latitude: {lat:.6f}\n")
    fout.write(f"Minor constituents inferred from {refstation}\n")
    fout.write(f"Starting time: {datetext}\n")
    fout.write(f"Time step: {options.interval:.2f} min  Length: {options.length:.2f} days\n")
    fout.write(f"Mean water level: {mean * (3.2808 if options.feet else 1):.2f} {'ft' if options.feet else 'm'}\n\n")
    fout.write(f"Predictions generated: {ctime()} (System)\n")
    fout.write(f"Heights in {'feet' if options.feet else 'meters'} above MLLW\n")

    if tzname == "UTC":
        fout.write(f"Prediction date and time in Universal Time (UTC)\n")
        fout.write(f"\nDate        Time  TZ{delim}Height\n")
    elif tzname == "Local":
        fout.write(f"Prediction date and time in Pacific Time (PST or PDT)\n")
        fout.write(f"\nDate        Time  TZ{delim}Height\n")
    else:
        fout.write("Prediction date and time in Julian Days (JD)\n")
        fout.write(f"\nDay{delim}Height\n")

# ----------------------------- Tide Printing -----------------------------
def print_tide_entry(fout, tide, options):
    jd = tide[0]
    height = tide[1]
    delim = options.delimiter
    height_str = f"{height * (3.2808 if options.feet else 1):.1f}" if options.feet else f"{height:.2f}"

    if options.pacific:
        jd_local, zone = ut_to_lt(jd)
        datetext = jd_to_ISO(jd_local, zone, "minute")
    elif options.julian:
        datetext = f"{jd:12.4f}"
    else:
        year, month, fday = jd_to_cal(jd)
        hour, minute, _ = fday_to_hms(fday)
        datetext = f"{year:04d}-{month:02d}-{int(fday):02d} {hour:02d}:{minute:02d} UTC"

    fout.write(f"{datetext}{delim}{height_str}\n")

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
    
    
#------------------------------------------------------------------------------
# calendar.py - A library of calendar functions
#
# Copyright 2000, 2001 William McClain
# Modified by David Finlayson (no longer depends on exogenous files)
#
# Reference: Jean Meeus, _Astronomical Algorithms_, second edition,
# 1998, Willmann-Bell, Inc.
#------------------------------------------------------------------------------ 
from math import *
from time import gmtime

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
      

      