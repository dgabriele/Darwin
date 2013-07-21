'''darwin.app'''

from collections import deque
import webob


class App(object):
  
  def __init__(self, root, **response_kwargs):
    self._response_kwargs = response_kwargs
    self.root = root
  
  def __call__(self, env, start_response):
    res = webob.Response(**self._response_kwargs)
    req = webob.Request(env)
    path = deque(req.path_info.lstrip('/').split('/'))
    if path[0] == 'favicon.ico':
      return res(env, start_response)
    elif path[0] == '':
      path.popleft()
    node_cls = self.root
    while path:
      key = path.popleft()
      next_cls = node_cls.children['literals'].get(key)
      if not next_cls:
        for regexp, cls in node_cls.children['regexps'].iteritems():
          if regexp.match(key):
            next_cls = cls
            break
      if not next_cls:
        raise KeyError()
      else:
        node_cls = next_cls
    node = node_cls(req, res)
    with node:
      getattr(node, req.method)()
      return res(env, start_response)
    

