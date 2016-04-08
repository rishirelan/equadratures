#!/usr/bin/python
import numpy as np
import math as mt
"""

    The IndexSet Class
    Designed to be the base class for all subsequent multivariate polynomials

    Pranay Seshadri
    ps583@cam.ac.uk

"""
class IndexSet(object):
    """ An index set.
    Attributes:
        index_set_type: Choose between:
                        a. Tensor grid
                        b. Total order index set
                        c. Hyperbolic cross space
                        d. Sparse grids

        orders: Maximum orders in each direction
        level: [For sparse grids only] "density of points"
        growth_rule: scaling up of points between levels:
                        a. Linear growth rule
                        b. Exponential growth rule


       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                constructor / initializer
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""

    def __init__(self, index_set_type, orders, level=None, growth_rule=None):
        self.index_set_type = index_set_type # string
        self.orders =  orders # we store order as an array!

        # Check for the levels (only for sparse grids)
        if level is None:
            self.level = []
        else:
            self.level = level

        # Check for the growth rule (only for sparse grids)
        if growth_rule is None:
            self.growth_rule = []
        else:
            self.growth_rule = growth_rule

    """~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                                get() methods
       ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"""
    def getIndexSetType(self):
        return self.index_set_type

    def getOrders(self):
        return self.orders

    def getIndexSet(self):
        dimensions = len(self.orders)
        name = self.index_set_type
        if name == "total order":
            index_set = total_order_index_set(self.orders)
        elif name == "sparse grid":
            index_set = sparse_grid_index_set(dimensions, self.level, self.growth_rule) # Note sparse grid rule depends on points!
        elif name == "tensor grid":
            index_set = tensor_grid_index_set(self.orders)
        elif name == "hyperbolic cross":
            index_set = hyperbolic_index_set(self.orders)
        else:
            index_set = [0]
        return index_set


def hyperbolic_index_set(orders):

    # Initialize a few parameters for the setup
    q = 1.0
    dimensions = len(orders)
    n_bar = tensor_grid_index_set(orders)
    n_new = []
    summation = np.ones((1, len(n_bar)))
    for i in range(0, len(n_bar)):
        array_entry = n_bar[i] ** q
        summation[0,i] = ( np.sum(array_entry)  ) ** (1.0/(1.0 * q)) # dimension correction!

    # Loop!
    for i in range(0, len(summation[0,:])):
        if( summation[0,i] <= np.max(orders) ):
            n_new.append(n_bar[i,:])

    # Now re-cast n_new as a regular array and not a list!
    hyperbolic_set = np.ones((len(n_new), dimensions))
    for i in range(0, len(n_new)):
        for j in range(0, dimensions):
            r = n_new[i]
            hyperbolic_set[i,j] = r[j]

    return hyperbolic_set

# Double checked April 7th, 2016 --> Works!
def total_order_index_set(orders):

    # For a total order index set, the sum of all the elements of a particular
    # order cannot exceed that of the polynomial.

    # Initialize a few parameters for the setup
    dimensions = len(orders)
    n_bar = tensor_grid_index_set(orders)
    n_new = [] # list; dynamic array

    # Now cycle through each entry, and check the sum
    summation = np.sum(n_bar, axis=1)
    for i in range(0, len(summation)):
        if(summation[i]  <= np.max(n_bar) ):
            value = n_bar[i,:]
            n_new.append(value)

    # But I want to re-cast this list as an array
    total_index = np.ones((len(n_new), dimensions))
    for i in range(0, len(n_new)):
        for j in range(0, dimensions):
            r = n_new[i]
            total_index[i,j] = r[j]

    return total_index



def sparse_grid_index_set(dimensions, level, growth_rule):

    # Initialize a few parameters for the setup
    lhs = level + 1
    rhs = level + dimensions

    # Set up a global tensor grid
    tensor_elements = np.ones((dimensions))
    for i in range(0, dimensions):
        tensor_elements[i] = int(rhs)

    n_bar = tensor_grid_index_set(tensor_elements) + 1

    # Check constraints
    n_new = [] # list; a dynamic array
    summation = np.sum(n_bar, axis=1)
    for i in range(0, len(summation)):
        if(summation[i] <= rhs  and summation[i] >= lhs):
            value = n_bar[i,:]
            n_new.append(value)

    # Sparse grid coefficients
    summation2 = np.sum(n_new, axis=1)
    a = [] # sparse grid coefficients
    for i in range(0, len(summation2)):
        k = int(level + dimensions - summation2[i])
        n = int(dimensions -1)
        value = (-1)**k  * (mt.factorial(n) / (1.0 * mt.factorial(n - k) * mt.factorial(k)) )
        a.append(value)

    # Now sort out the growth rules
    sparse_index = np.ones((len(n_new), dimensions))
    for i in range(0, len(n_new)):
        for j in range(0, dimensions):
            r = n_new[i]
            if(r[j] - 1 == 0):
                sparse_index[i,j] = int(1)
            elif(growth_rule is 'exponential' and  r[j] - 1 != 0 ):
                sparse_index[i,j] = int(2**(r[j] - 1) + 1 )
            elif(growth_rule is 'linear'):
                sparse_index[i,j] = int(r[j])
            else:
                raise KeyboardInterrupt

    # Ok, but sparse_index just has the tensor order sets to be used. Now we need
    # to get all the index sets!
    SG_indices = {}
    counter = 0
    for i in range(0, len(sparse_index)):
        SG_indices[i] = tensor_grid_index_set(sparse_index[i,:] )
        counter = counter + len(SG_indices[i])

    SG_set = np.zeros((counter, dimensions))
    counter = 0
    for i in range(0, len(sparse_index)):
        for j in range(0, len(SG_indices[i]) ):
            SG_set[counter,:] = SG_indices[i][j]
            counter = counter + 1

    return sparse_index, a, SG_set

def tensor_grid_index_set(orders):

    dimensions = len(orders) # number of dimensions
    I = [1.0] # initialize!

    # For loop across each dimension
    for u in range(0,dimensions):

        # Tensor product of the points
        vector_of_ones_a = np.ones((orders[u]+1, 1))
        vector_of_ones_b = np.ones((len(I), 1))
        counting = np.arange(0,orders[u]+1)
        counting = np.reshape(counting, (len(counting), 1) )
        left_side = np.array(np.kron(I, vector_of_ones_a))
        right_side = np.array( np.kron(vector_of_ones_b, counting) )  # make a row-wise vector
        I =  np.concatenate((left_side, right_side), axis = 1)

    # Ignore the first column of pp
    index_set = I[:,1::]

    return index_set
