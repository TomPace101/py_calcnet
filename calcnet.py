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

class CalcNode:
  """A node in a calculation network.

  A calculation node is defined by an expression that can be evaluated to produce a value.
  TODO: expressions are currently in python syntax, but this will change.
  TODO: the only variables currently allowed in an expression are single uppercase letters, but this will change.

  Attributes:

    - node_id = ID for this node, which may not be a string
    - reverse_deps = list of nodes that this node depends on
    - forward_deps = list of nodes that depend on this node
    - unsatisfied = integer number of unsatisfied reverse dependencies
      (This is set up and then used destructively during calculation order updates.)
    - up_to_date = boolean, False when the node needs to be re-calculated because of a change
    - discovered = boolean, True when previously discovered in a walk of the graph
    - expression = calculation expression for this node
    - value = result of the expression evaluation (None if not yet evaluated)
    - stage = integer identifying the calculation stage to which the node belongs"""
  def __init__(self,node_id,expression):
    self.node_id=node_id
    self.forward_deps=[]
    self.reverse_deps=[]
    self.unsatisfied=0
    self.up_to_date=False
    self.discovered=False
    self.stage=None
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

    The result is not returned, but is stored in self.value
    
    ##TODO: this uses python ``eval`` for now"""
    #Check for an empty formula
    if len(self.expression) == 0:
      self.value=None
    else:
      ##TODO: get the necessary variables into a dictionary
      ##parameters={}
      ##for k in self.reverse_deps:
      ##TODO
      ##self.value=eval(self._expression,parameters)
      #Value has now been updated
      ##self.up_to_date = True
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
    - ordering = the calculation order as a sequence of stages, each stage a group of nodes
    - num_stages = the total number of calculation stages"""
  def __init__(self,auto_recalc=True):
    #Set the level of automation
    self.auto_recalc=auto_recalc
    #Initialize adjacency dictionary
    self.adjacency={}
    #Set up the root node
    # The "node id" for the root node is ``None``.
    # This prevents conflict with a user-defined identifier,
    # and allows the default behavior of ``recalculate_from`` and related functions
    self.root_node=CalcNode(None,"")
    self.adjacency[None]=self.root_node
    #Set up the ordering
    self.root_node.stage=0
    self.ordering=[[None]]
    self.num_stages=1
    return
  @classmethod
  def load(cls,fpath):
    """Load a calculation network from a file

    The file should not include the root node.

    Arguments:

      - fpath = path to input file, as a string"""
    ##TODO: implement
    raise NotImplementedError("Loading from file not yet supported")
    net = cls()
    return net
  def save(self,fpath):
    """Write the calculation network to a file

    The output file will not include the root node.

    Arguments:

      - fpath = path to the output file, as a string"""
    ##TODO: implement
    raise NotImplementedError("Saving to file not yet supported")
    return
  def count(self):
    """Return a count of the number of nodes and the number of edges

    This will include the root node in the count of nodes,
    and its forward dependencies in the count of edges.

    Returns:

      - nodes = integer number of nodes
      - edges = integer number of edges

    >>> net = CalcNet(auto_recalc=False)
    >>> net.add_node("A","100")
    >>> net.add_node("B","A - 100")
    >>> net.add_node("C","A + B")
    >>> net.count()
    (4, 4)"""
    nodes=len(self.adjacency.keys())
    edges=0
    for node in self.adjacency.values():
      edges += len(node.forward_deps)
    return nodes, edges
  def add_node(self,node_id,expression):
    """Add a node to the calculation network
    
    >>> net = CalcNet(auto_recalc=False)
    >>> net.add_node("A","5")
    >>> net.adjacency["A"].expression == "5"
    True

    Ordering is updated incrementally as nodes are added.
    >>> net.add_node("B","A + 5")
    >>> net.adjacency["B"].stage
    2
    >>> net.add_node("C","B + 5")
    >>> net.ordering[3]
    ['C']
    >>> net.add_node("D","A - 5")
    >>> net.ordering[2]
    ['B', 'D']
    
    """
    self.adjacency[node_id]=CalcNode(node_id,expression)
    self.update_adjacencies(node_id)
    #Add to the appropriate calculation stage
    stage=self.compute_stage(node_id)
    self.adjacency[node_id].stage = stage
    if stage == self.num_stages:
      #Network needs a new stage
      self.ordering.append([node_id])
      self.num_stages += 1
    else:
      self.ordering[stage].append(node_id)
    #Evaluate node if requested
    #(All dependencies have to be satisfied to add a node, so nothing else needs to be updated)
    if self.auto_recalc:
      self.adjacency[node_id].evaluate()
    return
  def revise_node(self,node_id,expression):
    """Make a change to an existing node"""
    self.adjacency[node_id].expression=expression
    self.update_adjacencies(node_id)
    #Update the ordering
    ##TODO
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
  def compute_stage(self,node_id):
    """Compute the calculation stage number for the specified node

    The stages of the reverse dependencies are used for this calculation.
    If those stages are not already up-to-date, the stage returned here will be wrong."""
    if len(self.adjacency[node_id].reverse_deps)==0:
      return 0
    else:
      return 1 + max([self.adjacency[nd].stage for nd in self.adjacency[node_id].reverse_deps])
  def walk(self,start_node_id=None,breadth_first=True):
    """Generator for iterating over all nodes descending from the given starting node.

    Arguments:

      - start_node_id = optional starting node ID.
        If not given, the root node is used.
      - breadth_first = boolean, True for breadth-first traversal, False for depth-first

    Yields node IDs for the adjacency dictionary.

    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("J","1")
    >>> net.add_node("I","1")
    >>> net.add_node("H","1")
    >>> net.add_node("G","1")
    >>> net.add_node("F","H + I + J - 1")
    >>> net.add_node("E","G + H + I + J - 2")
    >>> net.add_node("D","G + H + I - 1")
    >>> net.add_node("C","D + E + F + J - 4")
    >>> net.add_node("B","D + E + F + G - 4")
    >>> net.add_node("A","B + C + G + J - 4")
    >>> len([nd for nd in net.walk()])
    11
    >>> len([nd for nd in net.walk(breadth_first=False)])
    11

    """
    #Mark all nodes as undiscovered
    for node_id in self.adjacency.values():
      node_id.discovered=False
    #Seed the queue of nodes with the specified node.
    queue=collections.deque([start_node_id])
    #Traverse the graph until the queue of nodes is empty
    while len(queue)>0:
      #Get the next node from the queue
      if breadth_first:
        node_id = queue.popleft()
      else:
        node_id = queue.pop()
      #Yield this node
      yield node_id
      #Add the undiscovered forward dependencies to the queue
      undiscovered=[fd for fd in self.adjacency[node_id].forward_deps if not self.adjacency[fd].discovered]
      queue.extend(undiscovered)
      #Mark the undiscovered nodes as now discovered
      for child_id in undiscovered:
        self.adjacency[child_id].discovered = True
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
  def recalculate_from(self,start_node_id=None):
    """Perform a recalculation of the network starting from the given node ID.

    If no node ID is given, a recalculation of the entire network is performed"""
    #Trace the unsatisfied dependencies
    self._trace_unsatisfied(start_node_id)
    #Update the evaluation order
    self._update_evaluation_order_from(start_node_id)
    #Do the evaluations
    self._evaluate_from(start_node_id)
    return
  def _trace_unsatisfied(self,start_node_id=None):
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
    2

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
    >>> net.adjacency["M"].unsatisfied
    1
    >>> net.adjacency["P"].unsatisfied
    1
    >>> net.adjacency["Q"].unsatisfied
    1
    >>> net.adjacency["X"].unsatisfied
    2
    >>> net.adjacency["Z"].unsatisfied
    2
    """
    #Traverse descendants starting with the specified node.
    #The order of traversal (breadth-first or depth-first) doesn't matter.
    for parent_id in self.walk(start_node_id):
      #Mark the parent as needing update
      self.adjacency[parent_id].up_to_date=False
      #The child nodes are the forward dependencies of the parent
      #Add the parent node to the unsatisfied dependencies of all its immediate children
      for child_id in self.adjacency[parent_id].forward_deps:
        self.adjacency[child_id].unsatisfied += 1
    return
  def _confirm_all_satisfied(self):
    """Confirm that no nodes have unsatisfied dependencies remaining"""
    still_unsat=[nd for nd in self.adjacency.keys() if self.adjacency[nd].unsatisfied>0]
    if len(still_unsat)>0:
      err_msg="Failed to determine ordering. Possible cycle:"
      for nd in still_unsat:
        err_msg += "\n{}: {}".format(nd,self.adjacency[nd].unsatisfied)
      raise Exception(err_msg)
    return
  def _update_stage_labels(self,start_node_id=None):
    """Label the specified node and its descendants with a calculation stage

    If no starting node ID is given, the entire network is re-labeled
    
    This method assumes that ``_trace_unsatisfied`` has already been called
    for the same starting node.
    It's also a good idea to call ``_confirm_all_satisfied`` after calling this function``
    
    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("F","6")
    >>> net.add_node("G","7")
    >>> net.add_node("H","8")
    >>> net.add_node("I","9")
    >>> net.add_node("J","10")
    >>> net.add_node("C","F + I - 12")
    >>> net.add_node("D","H - 4")
    >>> net.add_node("E","J - 5")
    >>> net.add_node("B","D + F - J + 2")
    >>> net.add_node("A","B + C - E + G - 6")
    >>> net._trace_unsatisfied()
    >>> net._update_stage_labels()
    >>> net._confirm_all_satisfied()
    >>> net._collect_stages()
    >>> o=[stage.sort() for stage in net.ordering] #For presentation purposes only
    >>> net.ordering[0]
    [None]
    >>> net.ordering[1]
    ['F', 'G', 'H', 'I', 'J']
    >>> net.ordering[2]
    ['C', 'D', 'E']
    >>> net.ordering[3]
    ['B']
    >>> net.ordering[4]
    ['A']
    >>> net.adjacency["A"].stage
    4
    >>> net.num_stages
    5

    If the network contains a cycle, the attempt to order will fail.

    TODO: example with a cycle
    """
    #Initialization
    queue=collections.deque([start_node_id])
    #Loop until the queue is empty
    while len(queue)>0:
      #Go through the queue in FIFO order
      node_id = queue.popleft()
      #Get the new stage number for the starting node
      new_stage = self.compute_stage(node_id)
      #Did the stage change?
      ##TODO: is there a way to use this information?
      stage_changed = new_stage == self.adjacency[node_id].stage
      #Set new stage
      self.adjacency[node_id].stage = new_stage
      #Update overall number of stages if needed
      self.num_stages=max(self.num_stages,new_stage)
      #For each child node (each forward dependency)
      children_ids=self.adjacency[node_id].forward_deps
      for child_id in children_ids:
        #Remove the parent from the child's unsatisfied dependency count
        self.adjacency[child_id].unsatisfied -= 1
        #If the child now has no unsatisfied dependencies, add it to the queue
        if self.adjacency[child_id].unsatisfied == 0:
          queue.append(child_id)
    #Done
    return
  def _collect_stages(self):
    """Create the calculation order from the stage number of each node.
    
    This requires that the nodes already know their own stage numbers,
    and that the total number of stages is already known."""
    self.ordering=[[] for i in range(self.num_stages)]
    for node_id,node in self.adjacency.items():
      self.ordering[node.stage].append(node_id)
    return
  def _update_evaluation_order_from(self,start_node_id=None):
    """Update the evaluation order, starting from the given node.

    If no node ID is given, the evaluation order for the entire network is updated."""
    #Get the requested starting node
    start_node = self.adjacency[start_node_id]
    ##TODO
    raise NotImplementedError("Evaluation order update not yet implemented.")
    return
  def _evaluate_from(self,start_node_id=None):
    """Perform an evaluation of the nodes, starting from the given node
    
    Assumes the evaluation order is already up-to-date.
    If no node ID is given, all nodes are evaluated."""
    start_node = self.adjacency[start_node_id]
    ##TODO
    ##TODO: be sure not to try to evaluate the root node (or, abandon having two classes and do a quick no-op for the root instead)
    raise NotImplementedError("Network calculation not yet implemented.")
    return
