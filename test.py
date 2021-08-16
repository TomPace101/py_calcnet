"""Testing out some of the ideas"""

class CalcNet(dict):
  """A calculation network"""
  def __init__(self):
    #Set up the root node
    ##TODO
    ##self.root_node=
    #Set up the end node?
    ##TODO
    ##self.end_node=
  def add_node(self,node_id):
    """Add a node to the calculation network"""
    ##TODO
    pass
  def remove_node(self,node_id):
    """Remove a node from the calculation network"""
    ##TODO
    pass
  def full_order_update(self):
    """Update the evaluation order for the entire network"""
    self.partial_order_update(self.root_node)
  def partial_order_update(self,node_id):
    """Update the evaluation order starting from the given node"""
    ##TODO
    pass
  def full_evaluation(self):
    """Perform a full evaluation of the calculation network"""
    self.partial_evaluation(self.root_node)
  def partial_evaluation(self,node_id):
    """Perform a partial evaluation, starting from the given node
    
    Assumes the evaluation order is already up-to-date"""
    ##TODO
    pass

class CalcNode:
  def __init__(self,node_id,expression,network):
    """A node in a calculation network.

    Attributes:

      - node_id = ID string for this node
      - expression = calculation expression for this node
      - network = calculation network to which this node belongs
      - forward_deps = list of nodes that depend on this node
      - reverse_deps = list of nodes that this node depends on."""
    self.node_id=node_id
    self.forward_deps=[]
    self.reverse_deps=[]
    self.network=network
    self.update_expression(expression)
    return
  def revise_expression(self,expression):
    """Make a change to the expression for an existing node"""
    self.expression=expression
    #Parse the expression
    ##TODO
    #Get the new list of dependencies
    ##TODO
    #Compile the expression
    ##TODO
    #Update dependency graph
    ##TODO
    #Update evaluation order
    self.network.update_order()
    #Update calculation
    self.network.partial_evaluation(self.node_id)
