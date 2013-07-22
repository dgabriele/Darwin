'''Darwin "blog" app example'''

from datetime import datetime

from darwin.node import Node


class Home(Node):
  
  def __enter__(self):
    self.user = 'guest423' # in reality, authenticate user here.
    return self
  
  def GET(self):
    return 'Welcome Home!'


class News(Home):
  
  key = 'news'

  def GET(self):
    self.res.body = 'Welcome to the news!'


class Section(News):

  key = r'/(?P<section>[a-z]\w+)/'

  def GET(self):
    s = self.matchdict['section']
    self.res.body = 'Welcome to the {0} section!'.format(s)


class Date(Section):

  key = r'/(?P<y>\d+)/(?P<m>\d+)/(?P<d>\d+)/'

  def GET(self):
    m = self.matchdict
    d = datetime(int(m['y']), int(m['m']), int(m['d'])) 
    self.res.body = '''
      Articles in "{sec}" from {date} for user "{user}"
    '''.format(
      sec=m['section'], 
      date=d.strftime('%x'), 
      user=self.user
    )




if __name__ == '__main__':
  from paste import httpserver
  Home.configure('development.ini')
  httpserver.serve(Home.app, 'localhost', 8080)
