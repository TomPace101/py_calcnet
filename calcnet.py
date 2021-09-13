"""A network of calculations, with dependency tracking.

This is a fairly straightforward application of a Directed Acyclic Graph (DAG).

For now, test with:
``python -m doctest calcnet.py``
"""

#Stanard library imports
import collections
import csv

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
  >>> is_sorted([None, None, 1, 2, 3])
  True
  """
  if len(seq)<=1:
    return True
  else:
    #Compare each item in the list to the following item
    #``None`` is allowed at the start of the list
    start = 0
    last = seq[start]
    while last is None:
      start += 1
      last=seq[start]
    for i in range(start,len(seq)):
      itm=seq[i]
      res = (itm is not None) and (last <= itm)
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

  >>> c = [None, 2]
  >>> d = [1, 2, 3]
  >>> not_in_c, not_in_d = get_differences(c,d)
  >>> not_in_c
  [1, 3]
  >>> not_in_d
  [None]

  Returns:

    - not_in_a = elements in list b not in list a
    - not_in_b = elements in list a not in list b
  """
  assert is_sorted(list_a), "Received unsorted list A."
  assert is_sorted(list_b), "Received unsorted list B."
  idx_a=idx_b=0
  not_in_a=[]
  not_in_b=[]
  while idx_a < len(list_a) and idx_b < len(list_b):
    itm_a = list_a[idx_a]
    itm_b = list_b[idx_b]
    if itm_a == itm_b:
      idx_a += 1
      idx_b += 1
    elif (itm_a is None) or (itm_a < itm_b):
      not_in_b.append(itm_a)
      idx_a += 1
    elif (itm_b is None) or (itm_b < itm_a):
      not_in_a.append(itm_b)
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

  >>> CalcNode("A","5")
  <A, 5>

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
    - stage = integer identifying the calculation stage to which the node belongs
  """
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
  def __str__(self):
    return "<{}, {}>".format(self.node_id,self.expression)
  def __repr__(self):
    return str(self)
  def process_expression(self):
    """Read the expression to obtain the reverse dependencies

    TODO: compile the expression (not currently applicable)

    Returns:

      - reverse_deps = list of node ids for the reverse dependencies
    """
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
    #If there are no dependencies, link to the root node
    if len(reverse_deps)==0:
      reverse_deps=[None]
    #Compile the expression
    ##TODO: no compiled form for now
    return reverse_deps

class CalcNet:
  """A calculation network
  
  Attributes:
  
    - adjacency = adjacency dictionary for the graph of calculation nodes, {``node_id``: ``node``}
    - auto_recalc = Boolean, True to automatically recalculate on a change to a node
    - root_node = the root node of the calculation network:
        The reverse dependencies of all nodes eventually lead back to this one,
        and it has no reverse dependencies of its own.
        This node's dictionary entry is ``None``.
    - num_stages = the total number of calculation stages

  >>> exp_block=[
  ...   ("F","6"), ("G","7"), ("H","8"), ("I","9"), ("J","10"),
  ...   ("C","F + I - 12"), ("D","H - 4"), ("E","J - 5"),
  ...   ("B","D + F - J + 2"), ("A","B + C - E + G - 6")
  ... ]
  >>> net=CalcNet(auto_recalc=True, exp_block=exp_block)
  >>> net.adjacency["A"].value
  1
  >>> net.count()
  (11, 16)
  """
  metadata_attrs=['auto_recalc']
  metadata_separator="---"
  def __init__(self,auto_recalc=True,exp_block=None):
    """New calculation network, optionally with initial expressions

    Arguments:

      - auto_recalc = optional boolean for the object's ``auto_recalc`` attribute
      - exp_block = sequence of pairs (node ID, expression) to populate the network
    """
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
    self.num_stages=1
    #Add any provided nodes
    if exp_block is not None:
      self.insert_expressions(exp_block)
    return
  @classmethod
  def load_csv(cls,fpath):
    """Load a calculation network from a CSV file

    The file should not include the root node.

    Arguments:

      - fpath = path to input file, as a string
    """
    #Initialize without auto recalc
    net = cls(auto_recalc=False)
    #Store the eventual auto recalc setting
    auto_recalc = True
    #Open the file for reading
    with open(fpath,'r',newline='') as fp:
      rd=csv.reader(fp)
      section=0 #To keep track of which data section we're in
      #Go through each line
      for row in rd:
        #Section separators
        if len(row) == 1 and row[0]==cls.metadata_separator:
          section += 1
        #Process the metadata portion
        elif section == 0:
          assert row[0] in cls.metadata_attrs, "Invalid CalcNet attribute: {}".format(row[0])
          attr, val = row
          if attr == "auto_recalc":
            #Don't set auto_recalc now, just store it for later
            auto_recalc = val
          else:
            #Set the attribute
            setattr(net,attr,val)
        #Add all the expressions and set values
        elif section == 1:
          node_id, expression, value = row
          net.add_node(node_id,str(expression),process_forward_deps=False)
          net.adjacency[node_id].value = value
    #Now process all the forward dependencies
    net._set_all_forward_deps()
    #Set auto_recalc to the specified value
    net.auto_recalc = auto_recalc
    #If auto_recalc, evaluate
    if net.auto_recalc:
      net.recalculate_from()
    return net
  def save_csv(self,fpath):
    """Write the calculation network to a CSV file

    The output file will not include the root node.

    Arguments:

      - fpath = path to the output file, as a string

    If it already exists, the output file will be overwritten.
    """
    #Collect the stage order for the entire graph
    ordering = self._collect_stages()
    #Open the file for writing
    with open(fpath,"w",newline='') as fp:
      #Write in CSV format
      wr=csv.writer(fp)
      #Write network metadata
      for attr in self.metadata_attrs:
        wr.writerow([attr,getattr(self,attr)])
      #Separator row
      wr.writerow([self.metadata_separator])
      #Iterate over stages and nodes within each stage
      #Skip the root node
      for stage in ordering[1:]:
        #Not strictly necessary, but to make output order deterministic
        stage.sort()
        for node_id in stage:
          node = self.adjacency[node_id]
          #Write the node ID and its expression
          outrow=[node_id,node.expression,node.value]
          wr.writerow(outrow)
    #Done
    return
  def count(self):
    """Return a count of the number of nodes and the number of edges

    This will include the root node in the count of nodes,
    and its forward dependencies in the count of edges.

    Returns:

      - nodes = integer number of nodes
      - edges = integer number of edges
    """
    nodes=len(self.adjacency.keys())
    edges=0
    for node in self.adjacency.values():
      edges += len(node.forward_deps)
    return nodes, edges
  def add_node(self,node_id,expression,process_forward_deps=True):
    """Add a node to the calculation network

    Arguments:

      - node_id = ID of the node to add
      - expression = expression string for the node
      - process_forward_deps = optional boolean, passed to ``update_adjacencies``.
    
    >>> net = CalcNet(auto_recalc=False)
    >>> net.add_node("A","5")
    >>> net.adjacency["A"].expression == "5"
    True

    Ordering is updated incrementally as nodes are added.
    >>> net.add_node("B","A + 5")
    >>> net.adjacency["B"].stage
    2
    >>> net.add_node("C","B + 5")
    >>> net.adjacency["C"].stage
    3
    >>> net.add_node("D","A - 5")
    >>> net.adjacency["D"].stage
    2
    """
    assert node_id not in self.adjacency.keys(), "Node already exists: {}".format(node_id)
    self.adjacency[node_id]=CalcNode(node_id,expression)
    self.update_adjacencies(node_id,process_forward_deps)
    #Add to the appropriate calculation stage
    stage=self.compute_stage(node_id)
    self.adjacency[node_id].stage = stage
    if stage == self.num_stages:
      #Network needs a new stage
      self.num_stages += 1
    #Evaluate node if requested
    #(All dependencies have to be satisfied to add a node, so nothing else needs to be updated)
    if self.auto_recalc:
      self.evaluate_node(node_id)
    return
  def revise_node(self,node_id,expression):
    """Make a change to an existing node
    
    The calculation order is automatically updated when a node is changed.
    
    >>> exp_block = [
    ...   ("X","10"),
    ...   ("Y","X + 10"),
    ...   ("Z","X + 5"),
    ...   ("A","X + Y + Z")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
    >>> net.adjacency["Z"].stage
    2
    >>> net.adjacency["A"].stage
    3
    >>> net.revise_node("Z","Y + 10")
    >>> net.adjacency["Z"].stage
    3
    >>> net.adjacency["A"].stage
    4
    >>> net.adjacency["Y"].stage
    2
    >>> net.revise_node("Z","30")
    >>> net.adjacency["Z"].reverse_deps
    [None]
    >>> net.adjacency["Z"].stage
    1
    >>> net.adjacency["A"].stage
    3
    """
    self.adjacency[node_id].expression=expression
    self.update_adjacencies(node_id)
    #Update the ordering
    self._update_evaluation_order(node_id)
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
  def rename_node(self,old_id,new_id):
    """Change the ID of an existing node, and update dependencies accordingly

    Arguments:

      - old_id = old ID for the node
      - new_id = new ID for the node

    >>> exp_block=[
    ...   ("A","1"), ("B","1"), ("C","1"), ("D","1"),
    ...   ("E","A + B + C - 2"),
    ...   ("F","B + C + D - 2"),
    ...   ("G","E + F + A + D - 3"),
    ...   ("H","A + B + D + G - 3"),
    ...   ("I","E + F + G - 2"),
    ...   ("J","G + H + I - 2")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
    >>> net.rename_node("G","X")
    >>> "G" in net.adjacency.keys()
    False
    >>> net.adjacency["X"].forward_deps
    ['H', 'I', 'J']
    >>> net.adjacency["F"].forward_deps
    ['I', 'X']
    >>> net.adjacency["J"].reverse_deps
    ['H', 'I', 'X']
    """
    #Get the node itself
    node=self.adjacency[old_id]
    #Assign it to the new ID
    self.adjacency[new_id]=node
    node.node_id = new_id
    #Revise the forward dependencies of all the reverse dependencies
    for dep_id in node.reverse_deps:
      old_fwds=self.adjacency[dep_id].forward_deps
      self.adjacency[dep_id].forward_deps=[nd if nd != old_id else new_id for nd in old_fwds]
      self.adjacency[dep_id].forward_deps.sort()
    #Revise the expressions and reverse dependencies of all the forward dependencies
    for dep_id in node.forward_deps:
      new_exp = self.adjacency[dep_id].expression.replace(old_id,new_id)
      self.adjacency[dep_id].expression=new_exp
      old_revs=self.adjacency[dep_id].reverse_deps
      self.adjacency[dep_id].reverse_deps=[nd if nd != old_id else new_id for nd in old_revs]
      self.adjacency[dep_id].reverse_deps.sort()
    #Remove the old ID from the adjacency list
    self.adjacency.pop(old_id)
    #Done
    return
  def insert_expressions(self,exp_block,update_only=False,add_only=False,process_forward_deps=True):
    """Add or update expressions for a group of nodes

    Arguments:

      - exp_block = sequence of pairs (node_id, expression)
      - update_only = optional boolean, True to raise an error if any node IDs do not already exist
      - add_only = optional boolean, True to raise an error if any node IDs do already exist
      - process_forward_deps = optional boolean, passed to ``add_node`` for new nodes
      
    If both ``update_only`` and ``add_only`` are True,
    there will be an exception unless the expression block is completely empty.
    """
    for node_id,expression in exp_block:
      if node_id in self.adjacency.keys():
        if add_only:
          raise Exception("Node ID already exists: {}".format(node_id))
        self.revise_node(node_id,expression)
      else:
        if update_only:
          raise Exception("Node ID does not already exist: {}".format(node_id))
        self.add_node(node_id,expression,process_forward_deps)
    return
  def compute_stage(self,node_id):
    """Compute the calculation stage number for the specified node

    The stages of the reverse dependencies are used for this calculation.
    If those stages are not already up-to-date, the stage returned here will be wrong.
    """
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

    >>> exp_block=[
    ...   ("J","1"), ("I","1"), ("H","1"), ("G","1"),
    ...   ("F","H + I + J - 1"),
    ...   ("E","G + H + I + J - 2"),
    ...   ("D","G + H + I - 1"),
    ...   ("C","D + E + F + J - 4"),
    ...   ("B","D + E + F + G - 4"),
    ...   ("A","B + C + G + J - 4")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
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
  def _set_all_forward_deps(self):
    """Fill out all forward dependencies for the entire graph

    This is needed during loading operations, or any other time
    when nodes have been added with ``process_forward_deps=False``.

    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("A","0",process_forward_deps=False)
    >>> net.add_node("B","A + 1",process_forward_deps=False)
    >>> net.add_node("C","B + 1",process_forward_deps=False)
    >>> net.adjacency["A"].forward_deps
    []
    >>> net._set_all_forward_deps()
    >>> net.adjacency["A"].forward_deps
    ['B']
    >>> net.adjacency["B"].forward_deps
    ['C']
    """
    #Initialize all forward dependencies to empty
    for node in self.adjacency.values():
      node.forward_deps = []
    #For each node, use its reverse dependencies to set the forward dependencies of others
    for node_id,node in self.adjacency.items():
      for dep_id in node.reverse_deps:
        self.adjacency[dep_id].forward_deps.append(node_id)
    #Sort all forward dependencies
    for node in self.adjacency.values():
      node.forward_deps.sort()
    #Done
    return
  def update_adjacencies(self,node_id,process_forward_deps=True):
    """Update the reverse and forward dependencies from a single node

    Arguments:

      - node_id = ID of the node to update:
        Its own reverse dependencies will be updated, as well as the forward dependencies
        of those reverse dependencies.
      - process_forward_deps = optional boolean, True to update the forward dependency lists
        of all the reverse dependencies.
        This will raise an exception if any of the reverse dependencies
        in the expression do not already exist.

    >>> exp_block=[
    ...   ("A","5"), ("B","10"), ("C","15"), 
    ...   ("D","A + B + C")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
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
    #Find which dependencies are new, and which old dependencies have been removed
    old_back_nodes=self.adjacency[node_id].reverse_deps
    removed_deps,new_deps=get_differences(reverse_deps,old_back_nodes)
    #Update the reverse dependencies
    self.adjacency[node_id].reverse_deps=reverse_deps
    #Work with the forward dependency of other nodes, if requested
    if process_forward_deps:
      #Confirm that all the reverse dependencies are valid
      invalid_deps=[d for d in reverse_deps if d not in self.adjacency.keys()]
      assert len(invalid_deps)==0, "Invalid identifiers in expression for {}: {}".format(node_id,str(invalid_deps))
      #Add new dependencies to their forward list
      for dep_id in new_deps:
        self.adjacency[dep_id].forward_deps.append(node_id)
        #Keep the list sorted
        self.adjacency[dep_id].forward_deps.sort()
      #Remove deleted dependencies from their forward list
      for dep_id in removed_deps:
        fwd=self.adjacency[dep_id].forward_deps
        fwd.pop(fwd.index(node_id))
        #No need to re-sort because we're removing an item from a sorted list
    #Done
    return
  def _trace_unsatisfied(self,start_node_id=None):
    """Trace the unsatisfied dependencies in all descendants of the given node.

    Each node, including the start node, is also marked as needing recalculation,
    by setting the ``up_to_date`` value to False.

    >>> exp_block = [
    ...   ("A","5"),     ("B","A + 1"),
    ...   ("C","A + B"), ("D","A + B + C")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
    >>> net._trace_unsatisfied("B")
    >>> net.adjacency["D"].unsatisfied
    2

    If no node ID is given, all reverse dependencies are listed as unsatisfied.
    
    >>> exp_block=[
    ...   ("M","10"),    ("N","20"),
    ...   ("P","2 * M"), ("Q","3 * N"), ("R","N / M"),
    ...   ("X","P + Q"), ("Y","Q + R"), ("Z","N + Q")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
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
  def _update_stage_labels(self,start_node_id=None):
    """Label the specified node and its descendants with a calculation stage

    If no starting node ID is given, the entire network is re-labeled.
    
    This method assumes that ``_trace_unsatisfied`` has already been called
    for the same starting node.
    It's also a good idea to call ``_confirm_all_satisfied`` after calling this function``
    """
    #Initialization
    queue=collections.deque([start_node_id])
    #Loop until the queue is empty
    while len(queue)>0:
      #Go through the queue in FIFO order
      node_id = queue.popleft()
      #Get the new stage number for the starting node
      self.adjacency[node_id].stage = self.compute_stage(node_id)
      #Update overall number of stages if needed
      self.num_stages=max(self.num_stages,1+self.adjacency[node_id].stage)
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
  def _confirm_all_satisfied(self):
    """Confirm that no nodes have unsatisfied dependencies remaining"""
    ##TODO: should this accept a starting node ID, and walk, to reduce the number of nodes checked?
    still_unsat=[nd for nd in self.adjacency.keys() if self.adjacency[nd].unsatisfied>0]
    if len(still_unsat)>0:
      err_msg="Failed to determine ordering. Possible cycle:"
      for nd in still_unsat:
        err_msg += "\n{}: {}".format(nd,self.adjacency[nd].unsatisfied)
      raise Exception(err_msg)
    return
  def _update_evaluation_order(self,start_node_id=None):
    """Update the evaluation order, starting from the given node.

    If no node ID is given, the evaluation order for the entire network is updated.

    >>> exp_block=[
    ...   ("F","6"), ("G","7"), ("H","8"), ("I","9"), ("J","10"),
    ...   ("C","F + I - 12"), ("D","H - 4"), ("E","J - 5"),
    ...   ("B","D + F - J + 2"), ("A","B + C - E + G - 6")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
    >>> net._update_evaluation_order()
    >>> ordering = net._collect_stages()
    >>> o=[stage.sort() for stage in ordering] #For presentation purposes only
    >>> ordering[0]
    [None]
    >>> ordering[1]
    ['F', 'G', 'H', 'I', 'J']
    >>> ordering[2]
    ['C', 'D', 'E']
    >>> ordering[3]
    ['B']
    >>> ordering[4]
    ['A']
    >>> net.adjacency["A"].stage
    4
    >>> net.num_stages
    5

    If the network contains a cycle, the attempt to order will fail.

    TODO: example with a cycle
    """
    self._trace_unsatisfied(start_node_id)
    self._update_stage_labels(start_node_id)
    self._confirm_all_satisfied()
    return
  def _collect_stages(self,start_node_id=None):
    """Return the calculation order from the stage number of each node.
    
    This requires that the nodes already know their own stage numbers,
    and that the total number of stages is already known.

    Arguments:

      - start_node_id = optional node ID for the node from which the calculation will start

    If no node ID is given, the evaluation order for the entire network is included.

    Returns:

      - ordering = the calculation order as a sequence of stages, each stage a group of nodes

    >>> exp_block=[
    ...   ("A","1"),     ("B","A + 1"),
    ...   ("C","B + 1"), ("D","C + 1"),
    ...   ("E","D + 1"), ("F","D + 1")
    ... ]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
    >>> ordering = net._collect_stages("C")
    >>> ordering[0]
    ['C']
    >>> ordering[1]
    ['D']
    >>> ordering[2]
    ['E', 'F']
    """
    start_level=self.adjacency[start_node_id].stage
    ordering=[[] for i in range(self.num_stages - start_level)]
    for nd in self.walk(start_node_id):
      ordering[self.adjacency[nd].stage - start_level].append(nd)
    return ordering
  def evaluate_node(self, node_id):
    """Evaluate the expression for the specified node

    The result is not returned, but is stored in the ``value`` attribute of the node.

    All reverse dependencies must be evaluated first.
    
    ##TODO: this uses python ``eval`` for now
    
    >>> net=CalcNet(auto_recalc=False)
    >>> net.add_node("A","5")
    >>> net.add_node("B","A + 5")
    >>> net.evaluate_node("A")
    >>> net.adjacency["A"].value
    5
    >>> net.evaluate_node("B")
    >>> net.adjacency["B"].value
    10
    """
    #Get the node
    node = self.adjacency[node_id]
    #Check for an empty formula
    if len(node.expression) == 0:
      node.value=None
    else:
      #Get the values of all the reverse dependencies that are not the root node
      value_deps=[d for d in node.reverse_deps if d is not None]
      parameters={}
      for dep_id in value_deps:
        parameters[dep_id] = self.adjacency[dep_id].value
      #Evaluate
      node.value=eval(node.expression,parameters)
      #Value has now been updated
      node.up_to_date = True
    return
  def _evaluate_from(self,start_node_id=None):
    """Perform an evaluation of the nodes, starting from the given node
    
    Assumes the stage labeling of each node is already up-to-date.
    If no node ID is given, all nodes are evaluated.
    
    >>> exp_block=[("X","0"), ("Y","X + 1"), ("Z","Y + 1")]
    >>> net=CalcNet(auto_recalc=False,exp_block=exp_block)
    >>> net._evaluate_from("X")
    >>> net.adjacency["Z"].value
    2
    """
    #Get the nodes to recalculate grouped by stage
    ordering = self._collect_stages(start_node_id)
    #Go through the stages in order
    for stage in ordering:
      #TODO: all the nodes in a given stage can be evaluated in parallel
      for nd in stage:
        self.evaluate_node(nd)
    return
  def recalculate_from(self,start_node_id=None):
    """Perform a recalculation of the network starting from the given node ID.

    If no node ID is given, a recalculation of the entire network is performed
    """
    #Update the evaluation order
    self._update_evaluation_order(start_node_id)
    #Do the evaluations
    self._evaluate_from(start_node_id)
    return
