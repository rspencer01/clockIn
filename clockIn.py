#!/usr/bin/python

import os
import web
import datetime
import config

clock_in_dir = os.path.dirname(os.path.realpath(__file__))
database_config_file_path = os.path.join(clock_in_dir, 'config', 'database.cfg')
database_configuration = config.get_configuration(database_config_file_path)

db = web.database(**database_configuration)
# Todo: correct this
db.printing = False

current_job = -1


def get_logged_in():
    logged_in = 0
    global current_job
    last = list(db.query('SELECT * FROM work ORDER BY start DESC LIMIT 1'))
    if len(last) > 0:
        logged_in = last[0]['duration'] is None
    if logged_in:
        current_job = db.query(
            'SELECT jobs.* FROM work JOIN jobs ON work.job=jobs.id '
            'ORDER BY work.start DESC LIMIT 1')[0]
    return logged_in


def login_and_logout():
    logged_in = get_logged_in()
    if logged_in:
        db.update('work',
                  where='ISNULL(duration) AND user=1',
                  duration=web.SQLLiteral(
                      "UNIX_TIMESTAMP(NOW())-UNIX_TIMESTAMP(start)"))
        print 'Logging out', current_job.name
    else:
        if current_job == -1:
            print 'ERROR: Select job id with -j'
            return
        db.insert('work', start=web.SQLLiteral('NOW()'), user=1,
                  job=current_job)
        print 'Logging in',
        logged_in = get_logged_in()
        print current_job.name


def get_time_for_month(month, year, job=current_job):
    y = year + (month == 12 and 1 or 0)
    m = (month % 12) + 1
    DTS = str(year) + '-' + str(month) + '-01 00:00:00'
    nextDTS = str(y) + '-' + str(m) + '-01 00:00:00'
    seconds_this_month = \
        db.query("SELECT SUM(duration) AS uptime FROM work WHERE start< CAST('"
                 + nextDTS + "' AS DATETIME) AND start > CAST('"
                 + DTS + "' AS DATETIME) AND job="+str(job))[0]['uptime'] or 0
    return int(seconds_this_month)


def plurality(word, count):
    if count == 0 or count > 1:
        return word + 's'
    else:
        return word


def format_overview(label, time, hourly_rate):
    template = '{:13s} {:3d} {hour:5s} {:2d} {min:7s} (R {:4.2f})'
    hours = int(time / (60 * 60))
    minutes = int((time / 60) % 60)
    earnings = hourly_rate * time / (60 * 60)
    hour = plurality('hour', hours)
    minute = plurality('minute', minutes)
    return template.format(label, hours, minutes,
                           earnings, hour=hour, min=minute)


def display():
    logged_in = get_logged_in()
    if logged_in:
        print '\nCurrently logged in on job', current_job.name
        time = db.query('SELECT start FROM work '
                        'ORDER BY start DESC LIMIT 1')[0].start
        time_working = datetime.datetime.now() - time
        lgon = divmod(time_working.days * 86400 + time_working.seconds, 60)
        hours = lgon[0] / 60
        minutes = lgon[0] % 60
        seconds = lgon[1]
        print 'Logged in for', hours, plurality('hour', hours), minutes, \
            plurality('minute', minutes), 'and', \
            seconds, plurality('second', seconds)
        return
    else:
        print '\nCurrently logged out'
    if current_job == -1:
        return
    hourly_rate = db.select('jobs', where='id=' + str(current_job))[0].rate
    print '=' * 20
    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')
    year, month = now.year, now.month
    if month == 1:
        month, year = 13, year - 1
    month -= 1
    last_month = str(year) + '-' + str(month) + '-01 00:00'
    seconds_today = db.query("SELECT SUM(duration) AS uptime FROM work "
                             "WHERE start > CAST('" + today + "' AS DATETIME) "
                             "AND job=" + str(current_job))[0]['uptime'] or 0
    print format_overview('Today:', seconds_today, hourly_rate)
    print format_overview('This Month:',
                          get_time_for_month(now.month, now.year, current_job),
                          hourly_rate)
    print format_overview('Last Month:',
                          get_time_for_month(month, year, current_job),
                          hourly_rate)


def print_jobs():
    print '{:3s} | {:40s} | {:4s}'.format('Id', 'Name', 'Rate')
    print '-' * 53
    for i in db.select('jobs'):
        print '{id:3d} | {name:40s} | R{rate:3d}'.format(**i)


help = """ClockIn
=======

 -h Display this message
 -l Log in / out of a job
 -d Display hours worked in various timeframes
 -j The job number (required for some commands)"""


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Timekeeping for money.")
    parser.add_argument('-j', '--job', default=-1, type=int, help="The job ID")
    parser.add_argument('-d', '--display', action='store_true', help="Display job info")
    parser.add_argument('-l', action='store_true', help="Log in/out")
    parser.add_argument('-ls', action='store_true', help="List jobs")
    arguments = parser.parse_args()

    current_job = arguments.job

    if arguments.ls:
      print_jobs()

    if arguments.l:
        login_and_logout()

    if arguments.display:
        display()
