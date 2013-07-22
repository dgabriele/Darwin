Darwin
=============
A Phylogenetic Web Framework
--------------------------------------------

### Overview ###
In a nutshell, Darwin automatically maps Python inheritance hierarchies 
to corresponding URL traversals. There is no need to define extra "context" 
objects as you would in other frameworks. When Python loads a Darwin app, 
its automatically sets up a traversal tree.

![diagram](https://raw.github.com/basefook/Darwin/master/example.png)

This could be written

```python

class Home(darwin.Node):
  
  def __enter__(self):
    self.user = 'guest423' # in reality, authenticate the user here.
    return self
  
  @renderer('home')
  def GET(self):
    return {'user': self.user}


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
```
