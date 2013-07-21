from paste import httpserver
import darwin

class A(darwin.Node):
  pattern = ''
  def GET(self):
    self.res.body += 'A'

class B(A):
  pattern = 'foo'
  def GET(self):
    self.res.body += 'A/B'

class C(A):
  pattern = '/bar/'
  def GET(self):
    self.res.body += 'A/C'

app = darwin.App(A)
httpserver.serve(app, 'localhost', 8080)
