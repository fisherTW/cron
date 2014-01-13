#!/usr/bin/env python
# -*- coding: utf-8 -*-

import wsgiref.handlers
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import mail
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup

Config = { 
        'Sender'      : 'fisher.liao@gmail.com', #sender mail address
        'ToAddr'      : 'fisher_liao@genienrm.com', #destination mail address
        }

class Appdb(db.Model):
    appname = db.StringProperty()
    applimit = db.StringProperty()
    
class MainPage(webapp.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/html;charset=UTF-8'
    
    #load and delete prev data
    datas = Appdb.all().fetch(1,0)
    if datas:
      prevName = datas[0].appname
      prevLimit = datas[0].applimit
      datas[0].delete()
    else:
      prevName = "NULL"
      prevLimit = "NULL"

    url = 'http://freeappnow.jp/'
    html = urlfetch.fetch(url).content
    soup = BeautifulSoup(html)
    
    for s in soup('p', {'class':'present_info_appName'}):
      nowName = s.renderContents()
    for l in soup('p', {'class':'present_info_limit'}):
      for ls in soup('font', {'size':'36px'}):
        nowLimit = ls.renderContents()
	for i in soup('span', {'class':'present_info_icon'}):
		iconHtml = i.renderContents()
    	
    obj = Appdb(appname=nowName.decode('utf-8'),applimit=nowLimit.decode('utf-8'))
    obj.put()
        
    if prevName == nowName.decode('utf-8'):
      self.response.out.write('AppName:'+nowName.decode('utf-8'))
      self.response.out.write("""
"""+'Limit:'+nowLimit.decode('utf-8'))
    
    #send mail
    if prevName != nowName.decode('utf-8'):
      subject_text = '[FreeAppNow Notify] %s' % nowName.decode('utf-8')
      body_text = 'App:%s Limit:%s %s' % (nowName.decode('utf-8'), nowLimit.decode('utf-8'), iconHtml.decode('utf-8'))
      mail.send_mail(sender = Config['Sender'], 
          to = Config['ToAddr'],
          subject = subject_text, 
          body = body_text,
          )
    
def main():
  application = webapp.WSGIApplication([('/', MainPage)],
           debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
