"""A network of calculations, with dependency tracking."""

class CalcNet(dict):
  """A calculation network
  
  Attributes:
  
    - auto_recalc = Boolean, True to automatically recalculate on a change to a node
    - root_node = the root node of the calculation network:
        The reverse dependencies of all nodes eventually lead back to this one,
        and it has no reverse dependencies of its own.
        This node has no dictionary entry.
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
  def add_node(self,node_id):
    """Add a node to the calculation network"""
    ##TODO
    return
  def remove_node(self,node_id):
    """Remove a node from the calculation network"""
    ##TODO
    return
  def get_node
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
    start_node = self[node_id]
    ##TODO
    return
  def _evaluate_from(self,node_id=None):
    """Perform an evaluation of the nodes, starting from the given node
    
    Assumes the evaluation order is already up-to-date.
    If no node ID is given, all nodes are evaluated."""
    start_node = self[node_id]
    ##TODO
    return

class CalcNode:
  def __init__(self,node_id,expression,network):
    """A node in a calculation network.

    A calculation node is defined by an expression that can be evaluated to produce a value.
    TODO: expressions are currently in python syntax, but this will change.
    TODO: the only variables currently allowed in an expression are single uppercase letters, but this will change.

    Attributes:

      - node_id = ID string for this node
      - expression = calculation expression for this node
      - network = calculation network to which this node belongs
      - forward_deps = list of nodes that depend on this node
      - reverse_deps = list of nodes that this node depends on."""
    ##TODO: provide a default value for the network, since we expect only one network per document?
    self.node_id=node_id
    self.forward_deps=[]
    self.reverse_deps=[]
    self.network=network
    self.revise_expression(expression)
    return
  def revise_expression(self,expression):
    """Make a change to the expression for an existing node"""
    self.expression=expression
    #Parse the expression
    ##TODO: just use whitespace now
    parsed_expression=expression.split()
    #Get the new list of dependencies
    ##TODO: only allow single uppercase letters for now
    self.reverse_deps=[token for token in parsed_expression if ord(token)>=65 and ord(token<=90)]
    #Compile the expression
    ##TODO: no compiled form for now
    #Update the altered forward dependencies
    ##TODO
    #Recalculate if requested
    if self.auto_recalc:
      self.network.recalculate_from(self.node_id)
    #Done
    return