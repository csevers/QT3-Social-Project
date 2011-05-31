#soup.find(text=re.compile('Originally Posted by')).parent.strong.next

import mechanize
from BeautifulSoup import BeautifulSoup
from urlparse import urljoin
import re

class userCrawler:
  def __init__(self, userid):
    self.userid=str(userid)
    self.site = "http://www.quartertothree.com/game-talk/"
    self.br = mechanize.Browser()
    
  def getsoup(self):
    self.br.open(self.site)
    #response = mechanize.urlopen("http://www.quartertothree.com/game-talk/")
    #forms = mechanize.ParseResponse(response, backwards_compat=False)

    self.br.select_form(nr=0)
    self.br.form["vb_login_username"] = "user"
    self.br.form["vb_login_password"] = 'pass'
    print 'Logging in ....'
    response2 = br.submit()
  
    
    searchurl = urljoin(self.site, "search.php?do=finduser&u="+self.userid)
    print 'Getting ' + searchurl
    search = br.open(searchurl)
    self.soup = BeautifulSoup(search.read())


  def crawlUserThreads(self):
    links = self.soup('a', href=re.compile('showthread'))
    links = [x['href'] for x in links]
    site = "http://www.quartertothree.com/game-talk/"
    for link in links:
      
  
  
  
  
#nextpages = soup('a',href=re.compile('page='))
#links = soup('a', href=re.compile('showthread'))
#links[0]['href']
#soup2 = BeautifulSoup(blah.read())
