'''darwin.app'''

from collections import deque

import webob
import webob.exc


class App(object):
  
  def __init__(self, root_class, **response_kwargs):
    self._response_kwargs = response_kwargs
    self.root_class = root_class
  
  def __call__(self, env, start_response):
    ''' WSGI main point of entry for URL traversal.
    '''
    res = webob.Response(**self._response_kwargs)
    req = webob.Request(env)

    ''' 
      S:  path_info component substring sequence.
      s0: the first component of S.
      X:  the resolved node class to evaluate.
      X1: given X, X1 is an adjacent child node to resolve next.
      Xi: given X, Xi is an adjancent child node.
      x:  the evaluated instance of the fully resolved X.
      s:  S iterator.
    '''
    X = self.root_class
    S = deque(req.path_info.lstrip('/').split('/'))
    s0 = S[0]
    try:
      if s0 == 'favicon.ico': # TODO 
        return res(env, start_response)
      if s0 != '':
        while S:
          s = S.popleft()
          X1 = X.adj['literals'].get(s) # first, match against string literals,
          if not X1:
            for regex, Xi in X.adj['regexps'].iteritems(): # then regexps.
              if regex.match(s):
                X1 = Xi
                break
          if not X1:
            #raise KeyError('could not resolve URL path')
            raise webob.exc.HTTPTemporaryRedirect(location='/')
          else:
            X = X1
      with X(req, res) as x:
        getattr(x, req.method)()
        return res(env, start_response)
    except webob.exc.HTTPException as e:
      return req.get_response(e)(env, start_response)
  
    

