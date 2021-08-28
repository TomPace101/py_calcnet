"""A network of calculations, with dependency tracking.

For now, test with:
``python -m doctest calcnet.py``
"""

#Stanard library imports
import collections

def is_sorted(seq):
  """Return True if the sequence is properly sorted

  Conceptually, this is the same as ``all([seq[i-1]<itm for i,itm in enumerate(seq[1:])])``,
  but it's more careful about zero-length lists and makes sure each element is only accessed once.

  >>> is_sorted([1,2,5,10,20])
  True
  >>> is_sorted([6,9,3,10])
  False

  Duplicates in the sequence are allowed.

  >>> is_sorted([1,2,2,3])
  True

  Special cases:

  >>> is_sorted([100])
  True
  >>> is_sorted([])
  True

  """
  if len(seq)<=1:
    return True
  else:
    #Compare each item in the list to the following item
    last=seq[0]
    for i in range(1,len(seq)):
      itm=seq[i]
      res = last <= itm
      if not res:
        break
      last = itm
  return res

def get_uniques(seq):
  """Return a list of the unique items in a a sorted sequence.

  >>> get_uniques([1,2,2,3])
  [1, 2, 3]
  >>> get_uniques([99])
  [99]
  >>> get_uniques([])
  []

  """
  if len(seq)<=1:
    return seq
  else:
    last=seq[0]
    out=[last]
    for itm in seq[1:]:
      if itm != last:
        last=itm
        out.append(last)
    return out

def get_differences(list_a,list_b):
  """For two sorted lists a and b, find the elements in each not in the other

  Conceptually, this is the same as

    ``not_in_a=[x for x in list_b if x not in list_a]``
    ``not_in_b=[x for x in list_a if x not in list_b]``

  But that would have quadratic time complexity.
  The algorithm here is linear in the number of elements, but requires the lists to be previously sorted,
  so the overall complexity is n log n.

  >>> a = [0,1,3,4,5,7,9]
  >>> b = [0,2,3,4,6,7,8]
  >>> not_in_a, not_in_b = get_differences(a,b)
  >>> not_in_a
  [2, 6, 8]
  >>> not_in_b
  [1, 5, 9]

  Returns:

    - not_in_a = elements in list b not in list a
    - not_in_b = elements in list a not in list b"""
  assert is_sorted(list_a), "Received unsorted list A."
  assert is_sorted(list_b), "Received unsorted list B."
  idx_a=idx_b=0
  not_in_a=[]
  not_in_b=[]
  while idx_a < len(list_a) and idx_b < len(list_b):
    if list_a[idx_a] == list_b[idx_b]:
      idx_a += 1
      idx_b += 1
    elif list_a[idx_a] < list_b[idx_b]:
      not_in_b.append(list_a[idx_a])
      idx_a += 1
    elif list_b[idx_b] < list_a[idx_a]:
      not_in_a.append(list_b[idx_b])
      idx_b += 1
    else:
      raise Exception("This should not have happened.")
  if len(list_a) > idx_a:
    not_in_b += list_a[idx_a:]
  if len(list_b) > idx_b:
    not_in_a += list_b[idx_b:]
  return not_in_a, not_in_b

class BaseNode:
  """A node without an expression, used only for the dependency graph

  Attributes:

    - node_id = ID for this node, which may not be a string
    - reverse_deps = list of nodes that this node depends on
    - forward_deps = list of nodes that depend on this node
    - unsatisfied = list of unsatisfied reverse dependencies
      (This is set up and then used destructively during calculation order updates.)
    - up_to_date = boolean, False when the node needs to be re-calculated because of a change"""
  def __init__(self,node_id):
    self.node_id=node_id
    self.forward_deps=[]
    self.reverse_deps=[]
    self.unsatisfied=[]
    self.up_to_date=False
    return

class CalcNode(BaseNode):
  """A node in a calculation network.

  A calculation node is defined by an expression that can be evaluated to produce a value.
  TODO: expressions are currently in python syntax, but this will change.
  TODO: the only variables currently allowed in an expression are single uppercase letters, but this will change.

  Attributes in addition to BaseNode:

    - expression = calculation expression for this node
    - value = result of the expression evaluation (None if not yet evaluated)"""
  def __init__(self,node_id,expression):
    super().__init__(node_id)
    self.expression=expression
    self.value=None
    return
  def process_expression(self):
    """Read the expression to obtain the reverse dependencies

    TODO: compile the expression (not currently applicable)

    Returns:

      - reverse_deps = list of node ids for the reverse dependencies"""
    ##TODO: just use whitespace now
    parsed_expression=self.expression.split()
    #Get the new list of dependencies
    ##TODO: only allow single uppercase letters for now
    candidates=[token for token in parsed_expression if len(token)==1]
    new_deps=[token for token in candidates if ord(token)>=65 and ord(token)<=90]
    #Sort for later efficiency
    new_deps.sort()
    #Remove duplications so items are unique
    reverse_deps=get_uniques(new_deps)
    #Compile the expression
    ##TODO: no compiled form for now
    return reverse_deps
  def evaluate(self):
    """Evaluate the expression
    
    ##TODO: this uses python ``eval`` for now"""
    ##TODO: get the necessary variables into a dictionary
    ##parameters={}
    ##for k in self.reverse_deps:
    ##TODO
    ##self.value=eval(self._expression,parameters)
    raise NotImplementedError("Evaluation not yet implemented.")
    return

class CalcNet:
  """A calculation network
  
  Attributes:
  
    - adjacency = adjacency dictionary for the graph of calculation nodes, {``node_id``: ``node``}
    - auto_recalc = Boolean, True to automatically recalculate on a change to a node
    - root_node = the root node of the calculation network:
        The reverse dependencies of all nodes eventually lead back to this one,
        and it has no reverse dependencies of its own.
        This node's dictionary entry is ``None``.
    - ordering = the calculation order as a sequence of stages, each stage a group of nodes"""
  def __init__(self,auto_recalc=True):
    #Set the level of automation
    self.auto_recalc=auto_recalc
    #Initialize adjacency dictionary
    self.adjacency={}
    #Set up the root node
    # The "node id" for the root node is ``None``.
    # This prevents conflict with a user-defined identifier,
    # and allows the default behavior of ``recalculate_from`` and related functions
    self.root_node=BaseNode(None)
    self.adjacency[None]=self.root_node
    #Set up the ordering
    self.ordering=[]
    return
  def add_node(self,node_id,expression):
    """Add a node to the calculation network
    
    >>> net = CalcNet(auto_recalc=False)
    >>> net.add_node("A","5")
    >>> net.adjacency["A"].expression == "5"
    True
    
    """
    self.adjacency[node_id]=CalcNode(node_id,expression)
    self.update_adjacencies(node_id)
    #Evaluate node if requested
    #(All dependencies have to be satisfied to add a node, so nothing else needs to be updated)
    if self.auto_recalc:
      self.adjacency[node_id].evaluate()
    return
  def revise_node(self,node_id,expression):
    """Make a change to an existing node"""
    self.adjacency[node_id].expression=expression
    self.update_adjacencies(node_id)
    #Recalculate if requested
    if self.auto_recalc:
      self.recalculate_from(node_id)
    return
  def remove_node(self,node_id):
    """Remove a node from the calculation network
    
    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("X","10")
    >>> net.remove_node("X")
    >>> "X" in net.adjacency.keys()
    False

    Only nodes that no other nodes depend on can be removed.

    >>> net.add_node("Y","20")
    >>> net.add_node("Z","Y + 10")
    >>> net.remove_node("Y")
    Traceback (most recent call last):
    AssertionError: Cannot remove Y because other nodes depend on it: ['Z'].

    """
    #Make sure nothing depends on this node
    fwd=self.adjacency[node_id].forward_deps
    assert len(fwd) == 0, "Cannot remove {} because other nodes depend on it: {}.".format(node_id, str(fwd))
    #Remove the node from the adjacency list
    self.adjacency.pop(node_id)
    return
  def walk(self,node_id=None,breadth_first=True):
    """Generator for iterating over all nodes descending from the given starting node.

    Arguments:

      - node_id = optional starting node ID.
        If not given, the root node is used.
      - breadth_first = boolean, True for breadth-first traversal, False for depth-first

    Yields node IDs for the adjacency dictionary.

    """
    #Seed the queue of nodes with the specified node.
    queue=collections.deque([node_id])
    #Traverse the graph (breadth-first) until the queue of nodes is empty
    while len(queue)>0:
      #Get the next node from the queue
      if breadth_first:
        nd = queue.popleft()
      else:
        nd = queue.pop()
      #Yield this node
      yield nd
      #Add the forward dependencies to the queue
      queue.extend(self.adjacency[nd].forward_deps)
  def update_adjacencies(self,node_id):
    """Update the reverse and forward dependencies from a single node
    
    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("A","5")
    >>> net.add_node("B","10")
    >>> net.add_node("C","15")
    >>> net.add_node("D","A + B + C")
    >>> net.adjacency["D"].reverse_deps
    ['A', 'B', 'C']
    >>> net.adjacency["A"].forward_deps
    ['D']

    Nodes that have no reverse dependencies will connect back to the root node.

    >>> net.adjacency["A"].reverse_deps
    [None]
    
    """
    #Get the list of reverse dependencies
    reverse_deps=self.adjacency[node_id].process_expression()
    if len(reverse_deps)==0:
      reverse_deps=[None] #If no dependencies, link to the root node
    #Confirm that all the reverse dependencies are valid
    invalid_deps=[d for d in reverse_deps if d not in self.adjacency.keys()]
    assert len(invalid_deps)==0, "Invalid identifiers in expression for {}: {}".format(node_id,str(invalid_deps))
    #Find which dependencies are new, and which old dependencies have been removed
    old_back_nodes=self.adjacency[node_id].reverse_deps
    removed_deps,new_deps=get_differences(reverse_deps,old_back_nodes)
    #Update the reverse dependencies
    self.adjacency[node_id].reverse_deps=reverse_deps
    #Add new dependencies to their forward list
    for dep_id in new_deps:
      self.adjacency[dep_id].forward_deps.append(node_id)
      #Keep the list sorted
      self.adjacency[dep_id].forward_deps.sort()
    #Remove deleted dependencies from their forward list
    for dep_id in removed_deps:
      fwd=self.adjacency[dep_id].forward_deps
      fwd.pop(fwd.index(dep_id))
      #No need to re-sort because we're removing an item from a sorted list
    #Done
    return
  def recalculate_from(self,node_id=None):
    """Perform a recalculation of the network starting from the given node ID.

    If no node ID is given, a recalculation of the entire network is performed"""
    #Trace the unsatisfied dependencies
    self._trace_unsatisfied(node_id)
    #Update the evaluation order
    self._update_evaluation_order_from(node_id)
    #Do the evaluations
    self._evaluate_from(node_id)
    return
  def _trace_unsatisfied(self,node_id=None):
    """Trace the unsatisfied dependencies in all descendants of the given node.

    Each node, including the start node, is also marked as needing recalculation,
    by setting the ``up_to_date`` value to False.

    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("A","5")
    >>> net.add_node("B","A + 1")
    >>> net.add_node("C","A + B")
    >>> net.add_node("D","A + B + C")
    >>> net._trace_unsatisfied("B")
    >>> net.adjacency["D"].unsatisfied
    ['B', 'C']

    If no node ID is given, all reverse dependencies are listed as unsatisfied.
    
    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("M","10")
    >>> net.add_node("N","20")
    >>> net.add_node("P","2 * M")
    >>> net.add_node("Q","3 * N")
    >>> net.add_node("R","N / M")
    >>> net.add_node("X","P + Q")
    >>> net.add_node("Y","Q + R")
    >>> net.add_node("Z","N + Q")
    >>> net._trace_unsatisfied()
    >>> net.adjacency["P"].unsatisfied
    ['M']
    >>> net.adjacency["Q"].unsatisfied
    ['N']
    >>> net.adjacency["X"].unsatisfied.sort() #just for presentation; order doesn't matter internally
    >>> net.adjacency["X"].unsatisfied
    ['P', 'Q']
    >>> net.adjacency["Z"].unsatisfied.sort() #just for presentation ...
    >>> net.adjacency["Z"].unsatisfied
    ['N', 'Q']
    """
    #Traverse descendants starting with the specified node.
    #The order of traversal (breadth-first or depth-first) doesn't matter.
    for parent_id in self.walk(node_id):
      #Mark the parent as needing update
      self.adjacency[parent_id].up_to_date=False
      #The child nodes are the forward dependencies of the parent
      #Add the parent node to the unsatisfied dependencies of all its immediate children
      for child_id in self.adjacency[parent_id].forward_deps:
        self.adjacency[child_id].unsatisfied.append(parent_id)
    return
  def _update_evaluation_order_from(self,node_id=None):
    """Update the evaluation order, starting from the given node.

    If no node ID is given, the evaluation order for the entire network is updated."""
    #Get the requested starting node
    start_node = self.adjacency[node_id]
    ##TODO
    raise NotImplementedError("Evaluation order update not yet implemented.")
    return
  def _evaluate_from(self,node_id=None):
    """Perform an evaluation of the nodes, starting from the given node
    
    Assumes the evaluation order is already up-to-date.
    If no node ID is given, all nodes are evaluated."""
    start_node = self.adjacency[node_id]
    ##TODO
    raise NotImplementedError("Network calculation not yet implemented.")
    return
