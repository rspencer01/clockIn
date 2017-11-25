from datetime import datetime

import web

import clockIn
from models import db_session, Job, User, Work


def load_sqlalchemy(handler):
    web.ctx.orm = db_session
    try:
        return handler()
    except web.HTTPError:
        web.ctx.orm.commit()
        raise
    except:
        web.ctx.orm.rollback()
        raise
    finally:
        web.ctx.orm.commit()


urls = ('/', 'Index', '/invoice', 'Invoice')
render = web.template.render('templates/', base='layout')

app = web.application(urls, globals())
app.add_processor(load_sqlalchemy)


class Index:
    def GET(self):
        all_jobs = Job.query.all()

        job_id = web.input(job=None).job
        selected_job = Job.query.filter_by(id=job_id).first()

        details = clockIn.display(job_id)

        return render.index(
            details,
            all_jobs=all_jobs,
            selected_job=selected_job,
        )


class Invoice:
    def GET(self):
        today = datetime.utcnow()
        web_input = web.input()

        month = web.intget(web_input.get('month'), today.month)
        year = web.intget(web_input.get('year'), today.year)

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

        job_id = web.intget(web_input.get('job'), 1)

        actions = Work.query.filter(
            Work.start > this_month_datetime,
            Work.start < next_month_datetime,
            Work.job_id == job_id,
        ).all()

        total = clockIn.get_time_for_month(month, year, job_id)

        # Get user id. Default to the first user in the db
        user_id = web.intget(web_input.get('user'), 1)
        user = User.query.filter_by(id=user_id).first()
        job = Job.query.filter_by(id=job_id).first()

        detailed_invoice = 'detailed' in web.input()

        invoice_template = web.template.frender('templates/invoice.html')

        return invoice_template(
            actions=actions,
            month=month,
            year=year,
            detailed=detailed_invoice,
            total=total,
            job=job,
            user=user,
        )


if __name__ == '__main__':
    app.run()
