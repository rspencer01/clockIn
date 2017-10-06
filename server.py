import subprocess

import clockIn

import web

urls = ('/', 'index', '/invoice', 'invoice')

app = web.application(urls, globals())

render = web.template.render('templates/', base='layout')


class index:
    def GET(self):
        details = subprocess.Popen(
            ['clockIn', '-d'],
            stdout=subprocess.PIPE
        ).communicate()[0]

        return render.index(details)


class invoice:
    def GET(self):
        month = int(web.input().month)
        year = int(web.input().year)
        this_month_datetime = '{year}-{month}-01 00:00:00'.format(
            year=year,
            month=month
        )

        next_month = (month % 12) + 1
        next_month_year = year + (1 if month == 12 else 0)
        next_month_datetime = '{year}-{month}-01 00:00:00'.format(
            year=next_month_year,
            month=next_month
        )

        actions = clockIn.db.select(
            'work',
            where=(
                'start > $this_month '
                'AND start < $next_month '
                'AND JOB=$job'
            ),
            vars={
                'this_month': this_month_datetime,
                'next_month': next_month_datetime,
                'job': web.input().job
            }
        )
        total = clockIn.get_time_for_month(month, year, web.input().job)
        # job = clockIn.db.query('SELECT * FROM jobs WHERE id='+input().job)
        response = web.template.frender('templates/invoice.html')(
            list(actions),
            month,
            year,
            'detailed' in web.input(),
            total,
            clockIn.db.select('jobs', where={'id': web.input().job})[0]
        )

        return response


if __name__ == '__main__':
    app.run()
