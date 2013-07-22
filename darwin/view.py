'''darwin.view'''

import webob.exc


class renderer(object):
  '''
    A Mako "render to response" decorator. For example:
        
        class Home(Node):
          
          @renderer('home')
          def GET(self):
            return { ... }
          
  '''
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
      if node.template_lookup and isinstance(params, dict):
        template = renderer.template_lookup.get_template(self.path)
        node.res.text = template.render(**params)
      else:
        # TODO: log this event
        raise webob.exc.HTTPNotFound()
    return g 



