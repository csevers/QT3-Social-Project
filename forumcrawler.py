''' Some classes (only one at the moment) for getting information from online
    forums. 
    
    Author: Christopher Severs, chris.severs@gmail.com
    
'''

import mechanize 
from BeautifulSoup import BeautifulSoup 
from urlparse import urljoin 
import re 
from collections import deque 
import getpass 
from time import sleep


class vbforumcrawler:

  ''' A class to crawl and store data from quartertothree, or really any vbulletin
    forum. There are two main modes of operation. The first is user crawling, where
    a userid is specified and the crawler gets a list of threads that the specified
    user has posted in. Given this list of threads, the crawler then has another
    method which will get a list of users who posted in each thread and return the
    users who posted in each thread and the number of posts.
  
    The second mode of operation is getting a list of the top threads in each forum
    (this should be changed to be more flexible and allow any sorting in the
    future). There is then another method which will look in each thread and return
    all pairs of quoted-quoter posters.
  
    The crawler can be used either logged in as a user or not. Many boards require
    a user to be logged in to make use of the forum search functions. 
    
    Right now it is fairly chatty since I use it primarily in an interactive 
    fashion. 
    
    Everything is tuned to the quartertothree forums so some changes will likely
    be needed to make it work elsewhere. A more generic version is the end goal.
  
  '''

  pageque = None

  # Start a mechanize browser and login if desired. 
  # Input: option login boolean and site
  def __init__(self,login=False, site="http://www.quartertothree.com/game-talk/"): 
    self.site = site
    self.br = mechanize.Browser() 
    if(login):
      self.login()
    
  
  # Login script, check to see if the login was successful
  # TODO: Implement better login form detection and support for sending md5 of 
  #       password, as required by some vbulletin forums. 
  def login(self):
    self.br.open(self.site) 
    # this should be changed to detect the form more carefully
    self.br.select_form(nr=0)
    
    # need to add the MD5 login options 
    self.br.form["vb_login_username"] = raw_input("Username: ")
    self.br.form["vb_login_password"] = getpass.getpass() 
    print 'Logging in .... ',
    response2 = self.br.submit() 
    
    # simple check to see if the login worked
    # TODO: check the reason for login failure and notify
    if re.search('success', response2.read()):
      print "Success!" 
    else: 
      print "Failed!"
  
  
  # Get a requested page and return the BeautifulSoup, check for timeouts
  # Input: A string which is a partial URL to be joined to self.site
  # Output: A BeautifulSoup of the input page
  # TODO: More robust error handling (404, etc). 
  def getsoup(self, page): 
    print 'Getting ' + page 
    try: 
      search = self.br.open(page, timeout=30.0) 
      soup = BeautifulSoup(search.read()) 
    except mechanize.URLError:  # this might not be a timeout so it should be changed
      print 'Timed out, retrying ... ' 
      soup = self.getsoup(page)
    return soup
  
  # This method gets the entire list of threads a user has posted in
  # Input: a userid
  # Output: None, but it modifies self.pageque
  
  def getuserthreads(self, userid):
    # TODO: add support for a more generic searchurl
    searchurl = urljoin(self.site,"search.php?do=finduser&u="+userid) 
    
    # I get bored waiting if no neat text scrolls by
    print 'Getting ' + searchurl 
    search = self.br.open(searchurl) 
    soup = BeautifulSoup(search.read()) 
    
    # find all the links that point to new threads
    links = soup('a', href=re.compile('showthread\.php\?t=')) 
    
    # get the actual reference string
    links = [x['href'] for x in links]
    
    # see if there is another page of threads
    nextpage = soup('a', rel='next') 
    
    # keep getting threads while there is another page to visit
    while (len(nextpage) > 0): 
      temppage = urljoin(self.site, nextpage[0]['href']) 
      tempsoup = self.getsoup(temppage)
      templinks = tempsoup('a', href=re.compile('showthread\.php\?t='))
      links.extend([x['href'] for x in templinks]) 
      nextpage = tempsoup('a', rel='next')
      
    # finally, populate the pageque with the unique threads  
    # so far this doesn't need to be an actual queue, a stack would work
    # but having it as a queue leaves some options open
    self.pageque = deque(list(set(links))) 
  
  
  # Similar to getting the user threads, this method gets the top (in the sense of most replies)
  # threads in a given forum and timeframe
  # Input: An integer forum id and optional timeframe
  # Output: a list of thread id strings
  # TODO: Add support for other sorting options and next page crawling
  def getforumthreads(self,forum, timeframe=7):
  
    # TODO: break this into parts so each option can be specified as desired
    urlend= 'forumdisplay.php?f='+str(forum)+'&daysprune='+str(timeframe)+'&order=desc&sort=replycount' 
    forumurl = urljoin(self.site, urlend) 
    soup = self.getsoup(forumurl)
    threads = soup('a', id=re.compile('thread_title')) 
    self.pageque = deque([x['href'] for x in  threads])
  
  
  # This method gets pairs of quoted-quoter posters from a list of threads
  # Input: None, but self.pageque must have been populated
  # Output: a list of tuples representing a quoted-quoter interactions
  # TODO: check the quoted list against the poster list to filter out fake quotes
  def getquotes(self): 
    if not self.pageque: 
      raise ValueError, 'Page queue is empty!'
    edgelist = [] 
    # keep going until the queue runs out
    while(self.pageque): 
      # pause so as to not anger the forum hosts
      sleep(1)
      temppage = urljoin(self.site, self.pageque.pop()) 
      tempsoup = self.getsoup(temppage) 
      
      # quoted posts should include an 'Originally posted by line' 
      # TODO: Add a more robust way to find quotes
      posts = tempsoup(text=re.compile('Originally'))
      
      # Make sure we actually found some posts
      if posts: 
        
        # quoted usernames should appear between <strong> tags
        quoted = [x.parent.strong.next for x in posts if x.parent.strong] 
        
        # this one is a doozy
        # it finds the parent post table then gets the quoting username from that
        # with the assumption that the username for a post appears in an
        # <a> tag of class 'bigusername'
        quoters = [x.findParents('table',id=re.compile('post'))[0].find(
        'a',{'class':'bigusername'}).next for x in posts if x.parent.strong]
        
        # add the sorted quoted-quoter tuples to an edgelist
        # sorted since we don't distinguish direction
        # TODO: Maybe we want direction of edges, so this shouldn't be sorted
        edgelist.extend([tuple(sorted(x)) for x in zip(quoted,quoters)]) 
      
      # Once we've grabbed all the pairs on a page, check if there is a next
      # page to look at. If so, add it to the queue. 
      nextpage = tempsoup.find('a', rel='next') 
      if (nextpage):
        self.pageque.append(nextpage['href'])
      
    # return all the unique edge pairs
    return list(set(edgelist))
  
  
  
  # Similar to the getquotes, but this one gets all the users who have posted
  # in the threads in self.pageque
  # Input: None, but self.pageque must be populated
  # Output: A list of user dictionaries (one per thread) where the keys 
  #         are usernames and the values are post counts in the thread. 
  
  def getusers(self): 
    if not self.pageque: 
      raise ValueError, 'Page queue is empty!'
      
    users = []
    
    while (self.pageque): 
      # pause so as to not anger the forum hosts
      sleep(1) 
      
      # In this case we only want the actual thread id number
      # TODO: What if nothing is found?
      temppage = re.search('t=[0-9]*', self.pageque.popleft())
      
      # Use the nice whoposted feature to avoid having to crawl every page
      temppage = urljoin(self.site,'misc.php?do=whoposted&'+temppage.group() )
      tempsoup = self.getsoup(temppage) 
      
      # assume the usernames are in <a> tags with target _blank
      tempusers = tempsoup('a', target='_blank') 
      
      # assume the counts come right after the usernames in <a> tags
      tempcounts = [int(x.findNext('a').next) for x in tempusers] 
      
      tempusers = [x.next for x in tempusers] 
      
      # add the user:count pairs for the thread as a dictionary 
      users.append(dict(zip(tempusers,tempcounts))) 
   
    return users


