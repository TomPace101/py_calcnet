"""Testing out some of the ideas"""

class CalcNode:
  __all__={}
  def __init__(self,prop_id,expression):
    self.__all__[prop_id]=self
    self.prop_id=prop_id
    self.forward_deps=[]
    self.reverse_deps=[]
    self.update_expression(expression)
    return
  def update_expression(self,expression):
    self.expression=expression
    #Parse the expression
    ##TODO
    #Update dependency graph
    ##TODO
    #Update evaluation order
    ##TODO
    #Compile the expression
    ##TODO
    #Evaluate?
    ##TODO?
