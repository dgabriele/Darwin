'''darwin.node'''

import re
from collections import defaultdict


RE_REGEXP = re.compile(r'/(.+)/$')

class NodeType(type):
   
  def __new__(type_, name, bases, dict_):
    '''
      Assign to each class a table, partitioned into two groups: (1) string
      literals and (2) regular expressions. Each entry keys a subclass of the
      class currently being allocated. In other words, this function 
      automagically configures the URL traversal graph (a tree).
    '''
    cls = type.__new__(type_, name, bases, dict_)
    cls.children = defaultdict(dict)
    if hasattr(bases[0], 'children'):
      m = RE_REGEXP.match(cls.pattern)
      if m is not None:
        regexp = re.compile(m.groups()[0])
        bases[0].children['regexps'][regexp] = cls
      else:
        bases[0].children['literals'][cls.pattern] = cls
    return cls


class Node(object):
  
  __metaclass__ = NodeType
  
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
  




