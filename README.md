Darwin
=============
A Phylogenetic Web Framework
--------------------------------------------

### Overview ###
In a nutshell, Darwin automatically maps Python inheritance hierarchies 
to corresponding URL traversals. There is no need to define extra "context" 
objects as you would in other frameworks. When Python loads a Darwin app, 
its automatically builds the data structures used by URL traversals using
a special type constructor.

Consider the diagram below. When Darwin receives a request, it resolves
the URL path to the Date class. When instantiated, all necessary context 
data, like user session data, database tables, etc., are accumulated as
defined in the built-in \_\_enter\_\_ method of each inherited super-
class of the Date class.

Also, notice that request handler methods like GET, PUT, POST, etc. 
are also inherited. In the example below, suppose that the name of a 
news section is invalid. Since the Section class inherits the GET
handler of the News class, the default behavior is to respond with the
news view. In other words, inherited request handlers can be designed 
so that the behavior of your application decays gracefully in response 
to anomolous requests.

![diagram](https://raw.github.com/basefook/Darwin/master/example.png)

This could be written as follows:

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
    self.res.body = 'Welcome to Science & Technology News!'


class Section(News):

  key = r'/(?P<section>science|technology)/'

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
