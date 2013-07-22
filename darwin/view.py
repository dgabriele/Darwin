'''darwin.view'''

from mako.template import Template
from mako.lookup   import TemplateLookup

import webob.exc


class renderer(object):
  '''
    A "render to response" decorator. For example:
        
        class Home(Node):
          
          @renderer('home')
          def GET(self):
            return { ... }
          
  '''
  lookup = None # global TemplateLookup instance,
                # configured by root Node class.
  
  def __init__(self, name, ext='.mako'):
    '''
      Args:
        - name: the base file name of a template file
        - ext: the file extension for the template file.
    '''
    self.path = name + ext

  def __call__(self, f):
    def g(node):
      params = f(node)
      if renderer.lookup and isinstance(params, dict):
        template = renderer.lookup.get_template(self.path)
        node.res.text = template.render(**params)
      else:
        # TODO: log this event
        raise webob.exc.HTTPNotFound()
    return g 



