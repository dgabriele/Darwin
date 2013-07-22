'''darwin.node'''

import re
from collections import defaultdict, deque

import webob
import webob.exc


class NodeType(type):
   
  RE_REGEXP = re.compile(r'/(.+)/$')

  def __new__(type_, name, bases, dict_):
    '''
      Assign to each class a table, partitioned into two groups: (1) string
      literals and (2) regular expressions. Each entry keys a subclass of the
      class currently being allocated. In other words, this function 
      automagically configures the URL traversal graph (a tree).
    '''
    cls = type.__new__(type_, name, bases, dict_)
    cls.adj = defaultdict(dict)
    if hasattr(bases[0], 'key'):
      m = NodeType.RE_REGEXP.match(cls.key)
      if m is not None:
        regexp = re.compile(m.groups()[0])
        bases[0].adj['regexps'][regexp] = cls
      else:
        bases[0].adj['literals'][cls.key] = cls
    return cls


class Node(object):
  
  __metaclass__ = NodeType

  key = '' # doc root

  def __init__(self, req, res):
    self.req = req
    self.res = res

  def __enter__(self):
    '''
      Called during traveral. Set up and fetch any necessary data here before
      an HTTP method handler gets called.
    '''
    return self

  def __exit__(self, *args):
    '''
      Tear down anything you may have set up in __enter__.
    '''
    pass
  
  @classmethod
  def app(cls, env, start_response):
    ''' 
      WSGI main point of entry for URL traversal.
    '''
    res = webob.Response()
    req = webob.Request(env)

    ''' 
      p:    request path_info
      tail: p, after spliting of the head component
      s0:   the head component of p.
      X:    the resolved node class to evaluate.
      X1:   given X, X1 is an adjacent child node to resolve next.
      Xi:   given X, Xi is an adjancent child node.
      x:    the evaluated instance of the fully resolved X.
    '''
    X = cls
    p = req.path_info
    matchdict = {}
    try:
      s0, p = p.split('/', 1)
      if p == 'favicon.ico': # TODO: static handlers
        return res(env, start_response)
      while p:
        t = p.split('/', 1)
        s0, tail = t if len(t) == 2 else (t[0], '')
        X1 = X.adj['literals'].get(s0) 
        if not X1:
          for regex, Xi in X.adj['regexps'].iteritems(): 
            m = regex.match(p)
            if m:
              matchdict.update(m.groupdict())
              p = regex.split(p)[-1].lstrip('/')
              X1 = Xi
              break
        else:
          p = tail
        if not X1:
          raise webob.exc.HTTPTemporaryRedirect(location='/')
        else:
          X = X1
      x = X(req, res)
      x.matchdict = matchdict
      with x:
        getattr(x, req.method)()
        return res(env, start_response)
    except webob.exc.HTTPException as e:
      return req.get_response(e)(env, start_response)
  
    

  
  ## HTTP Method handlers ----------------------------------

  def GET(self):
    raise NotImplementedError('override in subclass')
  def PUT(self):
    raise NotImplementedError('override in subclass')
  def POST(self):
    raise NotImplementedError('override in subclass')
  def COPY(self):
    raise NotImplementedError('override in subclass')
  def DELETE(self):
    raise NotImplementedError('override in subclass')
  




