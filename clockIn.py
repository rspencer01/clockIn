#!/usr/bin/python
from datetime import datetime

from sqlalchemy import func

from models import Job, sqlalchemy_db, Work


current_job = -1


def get_logged_in():
    global current_job

    logged_in = False
    most_recent_work = Work.query.order_by(Work.start.desc()).first()

    if most_recent_work:
        logged_in = most_recent_work.duration is None

    if logged_in:
        current_job = Job.query.join(
            Work.job
        ).order_by(
            Work.start.desc()
        ).first()

    return logged_in


def login_and_logout():
    logged_in = get_logged_in()

    now = datetime.utcnow()

    if logged_in:
        with sqlalchemy_db() as session:
            current_work = Work.query.filter(
                Work.user_id == 1,
                Work.duration.is_(None)
            ).first()

            current_work.duration = (now - current_work.start).seconds
            session.add(current_work)

        print 'Logging out', current_job.name
    else:
        if current_job == -1:
            print 'ERROR: Select job id with -j'
            return

        with sqlalchemy_db() as session:
            new_work = Work(start=now, user_id=1, job_id=current_job)
            session.add(new_work)

        print 'Logging in',
        logged_in = get_logged_in()
        print current_job.name


def get_time_for_month(month, year, job=current_job):
    next_year = year + (month == 12 and 1 or 0)
    next_month = (month % 12) + 1

    dts = datetime(year, month, 1)
    next_dts = datetime(next_year, next_month, 1)

    with sqlalchemy_db():
        seconds_this_month = Work.query.with_entities(
            func.sum(Work.duration)
        ).filter(
            Work.start < next_dts,
            Work.start > dts,
            Work.job_id == job,
        ).scalar() or 0

    return float(seconds_this_month)


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


def display(job):
    to_display = ''
    logged_in = get_logged_in()

    if logged_in:
        to_display = '\nCurrently logged in on job %s' % current_job.name

        current_work = Work.query.order_by(Work.start.desc()).first()
        start_time = current_work.start
        time_working = datetime.utcnow() - start_time

        logon = divmod(time_working.days * 86400 + time_working.seconds, 60)
        hours = logon[0] / 60
        minutes = logon[0] % 60
        seconds = logon[1]
        to_display += '\nLogged in for {hours} {minutes} {seconds}'.format(
            hours='{} {}'.format(hours, plurality('hour', hours)),
            minutes='{} {}'.format(minutes, plurality('minute', minutes)),
            seconds='{} {}'.format(seconds, plurality('second', seconds))
        )
        return to_display
    else:
        to_display += '\nCurrently logged out'

    if job == -1:
        return to_display

    selected_job = Job.query.filter_by(id=job).first()
    if not selected_job:
        return 'Job %d does not exist' % job

    hourly_rate = selected_job.rate
    to_display += '\n' + '=' * 20

    now = datetime.utcnow()
    today = now.strftime('%Y-%m-%d')
    year, month = now.year, now.month

    if month == 1:
        month, year = 13, year - 1

    month -= 1
    last_month = datetime(year, month, 1)

    seconds_today = Work.query.with_entities(
        func.sum(Work.duration)
    ).filter(
        Work.start > today,
        Work.job == selected_job,
    ).scalar() or 0

    to_display += '\n' + format_overview('Today:', seconds_today, hourly_rate)
    to_display += '\n' + format_overview(
        'This Month:',
        get_time_for_month(now.month, now.year, job),
        hourly_rate
    )
    to_display += '\n' + format_overview(
        'Last Month:',
        get_time_for_month(last_month.month, last_month.year, job),
        hourly_rate
    )

    return to_display


def list_jobs():
    to_display = '{:3s} | {:40s} | {:4s}'.format('Id', 'Name', 'Rate')
    to_display += '\n' + '-' * 53

    for job in Job.query.all():
        to_display += (
            '\n{job.id:3d} | {job.name:40s} | R{job.rate:3d}'.format(job=job)
        )

    return to_display


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
        print list_jobs()

    if arguments.l:
        login_and_logout()

    if arguments.display:
        print display(current_job)
