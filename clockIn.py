#!/usr/bin/python

import sys,os
import argDec
import web
import datetime
import config

database_configuration = config.getConfiguration('/'.join(os.path.realpath(__file__).split('/')[:-1])+'/config/database.cfg')
db = web.database(**database_configuration)
# Todo: correct this
db.printing = False

currentJob = -1

def getLoggedIn():
  loggedIn = 0
  global currentJob
  last = list(db.query("SELECT * FROM work ORDER BY start DESC LIMIT 1"))
  if len(last)>0:
    loggedIn = last[0]['duration']==None
  if loggedIn:
    currentJob = db.query("SELECT jobs.* FROM work JOIN jobs ON work.job=jobs.id ORDER BY work.start DESC LIMIT 1")[0]
  return loggedIn

def loginout():
  loggedIn = getLoggedIn()
  if loggedIn:
    db.update("work",where='ISNULL(duration) AND user=1',duration=web.SQLLiteral("UNIX_TIMESTAMP(NOW())-UNIX_TIMESTAMP(start)"))
    print "Logging out",currentJob.name
  else:
    if currentJob==-1:
      print "ERROR: Select job id with -j"
      return
    db.insert("work",start=web.SQLLiteral("NOW()"),user=1,job=currentJob)
    print "Logging in",
    loggedIn = getLoggedIn()
    print currentJob.name

def getTimeForMonth(month,year,job=currentJob):
  y = year + (month==12 and 1 or 0)
  m = (month%12) + 1
  DTS = str(year)+'-'+str(month)+"-01 00:00:00"
  nextDTS = str(y)+'-'+str(m)+"-01 00:00:00"
  secondsThisMonth = db.query("SELECT SUM(duration) AS uptime FROM work WHERE start< CAST('"+nextDTS+"' AS DATETIME) AND start > CAST('"+DTS+"' AS DATETIME) AND job="+str(job))[0]["uptime"] or 0
  return int(secondsThisMonth)

def display():
  loggedIn = getLoggedIn()
  if loggedIn:
    print "\nCurrently logged in on job",currentJob.name
    time = db.query("SELECT start FROM work ORDER BY start DESC LIMIT 1")[0].start
    c = datetime.datetime.now() - time
    lgon = divmod(c.days * 86400 + c.seconds,60)
    print "Logged in for",lgon[0]/60,"hours",lgon[0],"minutes and",lgon[1],"seconds"
    return
  else:
    print "\nCurrently logged out"
  if currentJob==-1:
    return
  hourlyRate = db.select('jobs',where='id='+str(currentJob))[0].rate
  print '='*20
  now = datetime.datetime.now()
  today = now.strftime("%Y-%m-%d")
  y,m = now.year,now.month
  if m==1:m,y=13,y-1
  m-=1
  lastmonth = str(y)+'-'+str(m)+"-01 00:00"
  secondsToday = db.query("SELECT SUM(duration) AS uptime FROM work WHERE start > CAST('"+today+"' AS DATETIME) AND job="+str(currentJob))[0]["uptime"] or 0
  disp = lambda n,x: "{:13s} {:3d} hours {:2d} minutes (R {:4.2f})".format(n,int(x / (60 * 60)),int((x/60)%60),hourlyRate * x / (60*60))
  print disp("Today:",secondsToday)
  print disp("This Month:",getTimeForMonth(now.month,now.year,currentJob))
  print disp("Last Month:",getTimeForMonth(m,y,currentJob))

def printJobs():
  print "{:3s} | {:40s} | {:4s}".format('Id','Name','Rate')
  print '-'*53
  for i in db.select('jobs'):
    print "{id:3d} | {name:40s} | R{rate:3d}".format(**i)


help = """ClockIn
=======

 -h Display this message
 -l Log in / out of a job
 -d Display hours worked in various timeframes
 -j The job number (required for some commands)"""

if __name__=='__main__':
  args = argDec.argDec(sys.argv)
  currentJob = 'j' in args and args['j'] or -1
  if 'j' in args and args['j']==None:
    printJobs()

  if len(args) == 0 or 'h' in args:
    print help
    sys.exit(0)

  if 'l' in args:
    loginout()

  if 'd' in args:
    display()
