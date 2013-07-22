'''darwin.node'''

import re
from collections import defaultdict, deque
from ConfigParser import ConfigParser

import webob
import webob.exc


class NodeType(type):
   
  RE_REGEX = re.compile(r'/(.+)/$')

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
      m = NodeType.RE_REGEX.match(cls.key)
      if m is not None:
        regexp = re.compile(m.groups()[0])
        bases[0].adj['regexps'][regexp] = cls
      else:
        bases[0].adj['literals'][cls.key] = cls
    return cls


class Node(object):
  
  __metaclass__ = NodeType

  key = '' # doc root

  def __init__(self, req, res, matchdict={}):
    self.matchdict = matchdict
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
  def app(node_cls, env, start_response):
    ''' 
      WSGI main point of entry for URL traversal.
    '''
    res = webob.Response()
    path = env['PATH_INFO'].strip('/')

    if path == 'favicon.ico': # TODO: static handlers
      return res(env, start_response)

    req = webob.Request(env)
    matchdict = {}

    try:
      while path: 

        # 1. Split path into head & tail. EG, a/b/c -> (a, b/c).
        #
        splits = path.split('/', 1)
        head, tail = splits if len(splits) == 2 else (splits[0], '')

        # 2. Match head against adjacent string literals
        #
        next_node_cls = node_cls.adj['literals'].get(head) 

        # 3. Match unsegmented path head against adjacent regexps.
        #
        if not next_node_cls:
          for regex, child_node_cls in node_cls.adj['regexps'].iteritems(): 
            match = regex.match(path)
            if match:
              matchdict.update(match.groupdict())
              path = regex.split(path)[-1].lstrip('/')
              next_node_cls = child_node_cls
              break
        else:
          path = tail 

        # 4. Make sure a node class was resolved.
        #
        if not next_node_cls:
          raise webob.exc.HTTPNotFound()
        else:
          node_cls = next_node_cls

      # 5. Instantiate and call the resolved node.
      #
      with node_cls(req, res, matchdict) as node:
        getattr(node, req.method)()
        return res(env, start_response)

    except webob.exc.HTTPException as e:
      print e
      return req.get_response(e)(env, start_response)
  
  @classmethod
  def configure(cls, fpath=None, **settings):
    cp = ConfigParser(); cp.read(fpath)
    if cp.has_section('mako'):
      from darwin.view import renderer
      from mako.lookup import TemplateLookup
      if cp.has_option('mako', 'lookup-directories'):
        lookup_dirs = cp.get('mako', 'lookup-directories').split()
      else:
        lookup_dirs = None
      if cp.has_option('mako', 'module-directory'):
        module_dir = cp.get('mako', 'module-directory')
      else:
        module_dir = None
      lookup = TemplateLookup(lookup_dirs, module_dir)
      renderer.lookup = lookup

  
  ## HTTP Method handlers ----------------------------------

  def GET(self):
    raise webob.exc.HTTPNotFound()
  def PUT(self):
    raise webob.exc.HTTPNotFound()
  def POST(self):
    raise webob.exc.HTTPNotFound()
  def COPY(self):
    raise webob.exc.HTTPNotFound()
  def DELETE(self):
    raise webob.exc.HTTPNotFound()
  




