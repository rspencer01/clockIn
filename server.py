import web
import subprocess
import clockIn

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
        next_month = month % 12 + 1
        next_year = year + (month == 12 and 1 or 0)
        actions = clockIn.db.select('work',
                                    where='start>"' + str(year) + '-' +
                                          str(month) +
                                          '-01 00:00:00" AND start<"' +
                                          str(next_year) + '-' +
                                          str(next_month) +
                                          '-01 00:00:00" AND JOB=' +
                                          web.input().job)
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


if __name__ == "__main__":
    app.run()
