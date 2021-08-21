"""A network of calculations, with dependency tracking."""

class CalcNet:
  """A calculation network
  
  Attributes:
  
    - adjacency = adjacency dictionary for the graph of calculation nodes, {``node_id``: ``node``}
    - auto_recalc = Boolean, True to automatically recalculate on a change to a node
    - root_node = the root node of the calculation network:
        The reverse dependencies of all nodes eventually lead back to this one,
        and it has no reverse dependencies of its own.
        This node's dictionary entry is ``None``.
    - end_node = the end node of the calculation network
        The forward dependencies of all nodes eventually lead up to this one,
        and it has no forward dependencies of its own.
        This node has no dictionary entry."""
  def __init__(self):
    #Set the level of automation
    self.auto_recalc=True
    #Set up the root node
    ##TODO
    ##self.root_node=
    #The "node id" for the root node is `None`.
    # None is not a valid identifier, so there is no chance of a conflict with a user-defined identifier,
    # and this allows the default behavior of `recalculate_from` and related functions
    ##self[None]=self.root_node
    #Set up the end node?
    ##TODO
    ##self.end_node=
    return
  def add_node(self,node_id,expression):
    """Add a node to the calculation network"""
    self.adjacency[node_id]=CalcNode(node_id,expression)
    self.update_adjacencies(node_id)
    ##TODO
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
    """Remove a node from the calculation network"""
    ##TODO
    return
  def update_adjacencies(node_id):
    """Update the reverse and forward dependencies from a single node"""
    #Get the list of reverse dependencies
    reverse_deps=self.adjacency[node_id].parse_expression()
    #Confirm that all the reverse dependencies are valid
    invalid_deps=[d for d in reverse_deps if d not in self.adjacency.keys()]
    assert len(invalid_deps)==0, "Invalid identifiers in expression for {}: {}".format(node_id,str(invalid_deps))
    #Find which dependencies are new, and which old dependencies have been removed
    old_back_nodes=self.adjacency[node_id].reverse_deps
    ##TODO: this is O(n^2) in the number of dependencies: use a more efficient approach
    new_deps=[bid for bid in reverse_deps if bid not in old_back_nodes]
    removed_deps=[bid for bid in old_back_nodes if not in reverse_deps]
    #Add new dependencies to their forward list
    ##TODO
    #Remove deleted dependencies from their forward list
    ##TODO
    ##TODO: don't forget to sort any changed forward dependencies
    #Update the reverse dependencies
    self.adjacency[node_id].reverse_deps=reverse_deps
    #Done
    return
  def recalculate_from(self,node_id=None):
    """Perform a recalculation of the network starting from the given node ID.

    If no node ID is given, a recalculation of the entire network is performed"""
    #Update the evalulation order
    self._update_evaluation_order_from(node_id)
    #Do the evaluations
    self._evaluate_from(node_id)
    return
  def _update_evaluation_order_from(self,node_id=None):
    """Update the evaluation order, starting from the given node.

    If no node ID is given, the evaluation order for the entire network is updated."""
    #Get the requested starting node
    start_node = self.adjacency[node_id]
    ##TODO
    return
  def _evaluate_from(self,node_id=None):
    """Perform an evaluation of the nodes, starting from the given node
    
    Assumes the evaluation order is already up-to-date.
    If no node ID is given, all nodes are evaluated."""
    start_node = self.adjacency[node_id]
    ##TODO
    return

class CalcNode:
  def __init__(self,node_id,expression):
    """A node in a calculation network.

    A calculation node is defined by an expression that can be evaluated to produce a value.
    TODO: expressions are currently in python syntax, but this will change.
    TODO: the only variables currently allowed in an expression are single uppercase letters, but this will change.

    Attributes:

      - node_id = ID string for this node
      - expression = calculation expression for this node
      - reverse_deps = list of nodes that this node depends on.
      - forward_deps = list of nodes that depend on this node"""
    ##TODO: provide a default value for the network, since we expect only one network per document?
    self.node_id=node_id
    self.expression=expression
    self.forward_deps=[]
    self.reverse_deps=[]
    return
  def parse_expression(self):
    """Read the expression to obtain the reverse dependencies

    TODO: compile the expression (not currently applicable)

    Returns:

      - reverse_deps = list of node ids for the reverse dependencies"""
    ##TODO: just use whitespace now
    parsed_expression=expression.split()
    #Get the new list of dependencies
    ##TODO: only allow single uppercase letters for now
    reverse_deps=[token for token in parsed_expression if ord(token)>=65 and ord(token<=90)]
    #Sort for later efficiency
    reverse_deps.sort()
    ##TODO: remove duplications so items are unique
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
    return