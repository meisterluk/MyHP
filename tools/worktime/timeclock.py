#!/usr/bin/env python3

"""
    Work time logger
    ================

    Reads a work time logging file and prints the appropriate stats.
    A work time logging file is a plain text consists of lines such as:

        11.05.14 08:04-17:50  Some random text

    Meaning "I worked at the 14th of May 2011 between 8:04 am and 17:50 pm."
    The random text is left out and can be used for example to log the daily
    achievements. Please recognize that once a line is ended with
    "yy.mm.dd hh:mm" (a minus symbol might be left out) it is considered as
    last line the remaining time is calculated by this date.

    Note. Stats are unreliable whenever it is called before the beginning of
          the work day.
    Note. The software is thinking per week. So missing hours in the previous
          week will not have effect to the current one.
    Note. Pauses are ignored and cannot be entered.
    Note. This software is only for work times, which repeat themselves
          weekly.

    In the current version, the software tells you the following statistics:

    * (Week log) For each day: difference between planned work time and actual one
    * (Remaining) How much time to the end of the week is left
    * (Remaining) How long the current day should be at least
    * (Overall) How many hours, minutes and seconds you worked until today

    TODO:

    * Improve output handling
    * Make locale dependent
    * Improve configurability

    :project:   timeclock
    :author:    meisterluk
    :license:   Emailware
    :date:      Jul 2011
"""

import datetime
import sys

FILE = 'time.log'
PATTERN = '%Y.%m.%d %H:%M'
# probably an average work week
# in hours, 7 days (so, mo, tue, ... sat)
DAYS_DURATION = (0, 8, 8, 8, 8, 8, 0)

def get_days(seconds):
    """Get days (based on DAYS_DURATION) in seconds"""
    hours_per_week = sum(DAYS_DURATION)
    days = seconds / (hours_per_week * 3600)
    rem = seconds % (hours_per_week * 3600)
    for day in DAYS_DURATION:
        if (rem - day) > 0:
            rem = rem - day
            days += 1
        else:
            break
    return days

def line_parse(line):
    """Parse a single line. Provides datetime instances for start and end"""
    section = line.split()
    times = section[1].split('-')
    start = datetime.datetime.strptime \
        (section[0].strip() + ' ' + times[0], PATTERN)
    try:
        end = datetime.datetime.strptime \
            (section[0].strip() + ' ' + times[1], PATTERN)
    except ValueError:
        return (start, None)
    return (start, end)

def main(filename, deadline=None):
    """Main routine. Read file. Parse. Log. Render"""
    is_friday = datetime.datetime.today().weekday() == 4
    week_duration = sum(DAYS_DURATION)
    now = datetime.datetime.now()
    week_log, output = '', ''
    overall = 0
    remaining = datetime.timedelta(hours=0)

    with open(filename) as fp:
        for lineno, line in enumerate(fp.readlines()):
            try:
                start, end = line_parse(line)
            except (IndexError, ValueError):
                if line.strip() != "":
                    print("Invalid line found:", file=sys.stderr)
                    print("  " + line, file=sys.stderr)
                    print()
                continue
            print("Line {} successfully read. {} seconds.".format(lineno, int((end - start).total_seconds())))
            same_week = (start.isocalendar()[1] == now.isocalendar()[1])

            # termination
            if end is None:
                print("End is somehow None?!", file=sys.stderr)
                break

            # week_log
            if same_week and end is not None:
                week_log += "{0} {1} \n".format(start.strftime("%a"),
                    end - start - datetime.timedelta \
                    (hours=DAYS_DURATION[start.weekday()]))

            # remaining
            if same_week:
                remaining = (end - start)

            # overall
            overall += (end - start).total_seconds()

    # remaining
    remaining += (now - start)
    remaining = ((datetime.timedelta(hours=week_duration) - \
        remaining), (start + datetime.timedelta \
        (hours=DAYS_DURATION[start.weekday()]) - \
        datetime.timedelta(hours=sum(DAYS_DURATION \
        [0:start.weekday()]))))

    # OUTPUT

    # week_log
    if week_log:
        output += ("WEEK LOG \n"
                "-------- \n\n"
                + week_log + "\n")
    # remaining
    output += ("REMAINING \n"
               "--------- \n\n"
               "{0} until the end of the week \n\n"
               "{1} until the end of the current day \n\n"
               ).format(remaining[0], remaining[1].strftime('%c'))
    # overall
    output += ("TOTALLY DONE \n"
               "------------ \n\n"
               "{0:f} seconds \n"
               "{1:f} days \n"
               "{2:f} weeks \n\n").format(overall, get_days(overall), \
                    overall / (sum(DAYS_DURATION) * 3600))
    if deadline:
        deadline = datetime.datetime.strptime(deadline, PATTERN)
        until_deadline = deadline - now
        output += "Next deadline is in: {0}\n\n".format(until_deadline)
    return output


if __name__ == '__main__':
    if len(sys.argv) > 1:
        FILE = sys.argv[1]
    if len(sys.argv) > 2:
        DEADLINE = sys.argv[2]
    else:
        DEADLINE = None
    print(main(FILE, DEADLINE))
