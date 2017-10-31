#!/usr/bin/python
import datetime

import web

import config


db = web.database(**config.get_database_config())
# Todo: correct this
db.printing = False

current_job = -1


def get_logged_in():
    logged_in = 0
    global current_job
    last = list(db.select('work', order='start DESC', limit=1))

    if len(last) > 0:
        logged_in = last[0]['duration'] is None

    if logged_in:
        current_job = db.query(
            'SELECT jobs.* FROM work '
            'JOIN jobs ON work.job=jobs.id '
            'ORDER BY work.start DESC '
            'LIMIT 1'
        )[0]
    return logged_in


def login_and_logout():
    logged_in = get_logged_in()

    if logged_in:
        db.update(
            'work',
            where='ISNULL(duration) AND user=1',
            duration=web.SQLLiteral(
                'UNIX_TIMESTAMP(NOW())-UNIX_TIMESTAMP(start)'
            )
        )
        print 'Logging out', current_job.name
    else:
        if current_job == -1:
            print 'ERROR: Select job id with -j'
            return

        db.insert(
            'work',
            start=web.SQLLiteral('NOW()'),
            user=1,
            job=current_job
        )

        print 'Logging in',
        logged_in = get_logged_in()
        print current_job.name


def get_time_for_month(month, year, job=current_job):
    dts = '{year}-{month}-01 00:00:00'.format(year=year, month=month)

    next_year = year + (month == 12 and 1 or 0)
    next_month = (month % 12) + 1
    next_dts = '{next_year}-{next_month}-01 00:00:00'.format(
        next_year=next_year,
        next_month=next_month,
    )

    seconds_this_month = db.select(
        'work',
        what='SUM(duration) as uptime',
        where=(
            'start < CAST($next_dts AS DATETIME) '
            'AND start > CAST($dts AS DATETIME) '
            'AND job=$job'
        ),
        vars={
            'next_dts': next_dts,
            'dts': dts,
            'job': job,
        }
    )[0]['uptime'] or 0

    return int(seconds_this_month)


def plurality(word, count):
    if count == 0 or count > 1:
        return word + 's'
    else:
        return word


def format_overview(label, time, hourly_rate):
    hours = int(time / (60 * 60))
    hour_text = '{:3d} {:5s}'.format(hours, plurality('hour', hours))

    minutes = int((time / 60) % 60)
    minute_text = '{:2d} {:7s}'.format(minutes, plurality('minute', minutes))

    earnings = hourly_rate * time / (60 * 60)

    template = '{label:13s} {hours} {minutes} (R {earnings:4.2f})'
    return template.format(
        label=label,
        hours=hour_text,
        minutes=minute_text,
        earnings=earnings,
    )


def display():
    logged_in = get_logged_in()

    if logged_in:
        print '\nCurrently logged in on job', current_job.name

        start_time = db.select('work', order='start DESC', limit=1)[0].start
        time_working = datetime.datetime.now() - start_time

        logon = divmod(time_working.days * 86400 + time_working.seconds, 60)
        hours = logon[0] / 60
        minutes = logon[0] % 60
        seconds = logon[1]
        print 'Logged in for {hours} {minutes} {seconds}'.format(
            hours='{} {}'.format(hours, plurality('hour', hours)),
            minutes='{} {}'.format(minutes, plurality('minute', minutes)),
            seconds='{} {}'.format(seconds, plurality('second', seconds))
        )
        return
    else:
        print '\nCurrently logged out'

    if current_job == -1:
        return

    hourly_rate = db.select('jobs', where={'id': str(current_job)})[0].rate
    print '=' * 20

    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')
    year, month = now.year, now.month

    if month == 1:
        month, year = 13, year - 1

    month -= 1
    last_month = '{year}-{month}-01 00:00'.format(year=year, month=month)

    seconds_today = db.select(
        'work',
        what='SUM(duration) AS uptime',
        where='start > CAST($today AS DATETIME) AND job=$job',
        vars={'today': today, 'job': current_job}
    )[0]['uptime'] or 0

    print format_overview('Today:', seconds_today, hourly_rate)
    print format_overview(
        'This Month:',
        get_time_for_month(now.month, now.year, current_job),
        hourly_rate
    )
    print format_overview(
        'Last Month:',
        get_time_for_month(month, year, current_job),
        hourly_rate
    )


def print_jobs():
    print '{:3s} | {:40s} | {:4s}'.format('Id', 'Name', 'Rate')
    print '-' * 53

    for job in db.select('jobs'):
        print '{id:3d} | {name:40s} | R{rate:3d}'.format(**job)


help = """ClockIn
=======

 -h Display this message
 -l Log in / out of a job
 -d Display hours worked in various timeframes
 -j The job number (required for some commands)"""


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Timekeeping for money.')
    parser.add_argument('-j', '--job', default=-1, type=int, help='The job ID')
    parser.add_argument(
        '-d',
        '--display',
        action='store_true',
        help='Display job info'
    )
    parser.add_argument('-l', action='store_true', help='Log in/out')
    parser.add_argument('-ls', action='store_true', help='List jobs')
    arguments = parser.parse_args()

    current_job = arguments.job

    if arguments.ls:
        print_jobs()

    if arguments.l:
        login_and_logout()

    if arguments.display:
        display()
