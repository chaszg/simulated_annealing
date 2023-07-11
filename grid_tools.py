import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

#This function was modified with suggestions from ChatGPT

def generate_grid(rows, cols, percentage=50, seed=123):
    """
    Generates a two-dimensional matrix of randomized 0's and 1's 
    with dimensions `rows` x `cols`. `percentage` controls the 
    composition of 1's in the matrix (default: 50). `seed` controls
    the state of the random number generator for reproducibility.
    """
    np.random.seed(seed)
    grid = np.random.rand(rows, cols)
    grid = (grid <= percentage/100).astype(int)
    return grid


def plot_hot(grid):
    """
    Displays a heatmap of a two-dimensional matrix, `grid`.
    """
    plt.imshow(grid, cmap='hot', interpolation='nearest')
    plt.show()


#This function was modified with suggestions from ChatGPT

def random_grid_point(grid):
    """
    Returns a random pair of indices (x,y) for elements
    within the boundaries of the two-dimensional matrix, 
    `grid`.
    """
    x = np.random.randint(0, grid.shape[0])
    y = np.random.randint(0, grid.shape[1])
    return (x, y)


#This function was modified with suggestions from ChatGPT

def get_neighbors(x, y, rows, cols):
    """
    Returns a set of neighboring indices (`neighbors`) for an element 
    with indices (`x`,`y`) in a two-dimensional matrix with dimensions
    `rows` x `cols`. Only orthogonal neighbors (above/below, left/right)
    are considered. 
    
    A periodic boundary condition is applied so that 
    neighbors of indices at edges or corners are recognized on the 
    opposite side(s) of the matrix.
    """
    neighbors = set() #initialize empty set to add neighbor indices
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        new_x = (x+dx) % rows #modulo operation (%) employs periodic boundary condition if a neighbor is out of bounds
        new_y = (y+dy) % cols
        neighbors.add((new_x, new_y))
    return neighbors


def count_identical_neighbors(neighbors,grid_point,grid):
    """
    This function compares the value of an item (`grid_point`) in 
    a two-dimensional matrix (`grid`) to the values of items that 
    neighbor `grid_point`. Neighbors are identified using indices
    from the list, `neighbors`.
    
    For each neighbor that matches the value at `grid_point`, `count`
    increases by 1. The final result of count is returned. 
    
    0 <= `count` <=4
    """
    count = 0
    for n in neighbors:
        if grid_point == grid[n[0]][n[1]]:
            count += 1
    return count


def count_total_energy(grid):
    """
    Counts the number of identical neighbors for every element in
    a two-dimensional matrix `grid`. An "energy" quantity is calculated
    based on the number of identical neighbors to an element. For an
    element with fewer identical neighbors, the resulting energy quantity
    is lower (more favored, where 0 is most favorable). For an element 
    greater identical neighbors, the energy is higher (less favored, where
    4 is least favorable).
    
    Energy quantities are summed for every element in `grid` to calculate 
    the total energy of the system and is returned as `total_energy`.
    """
    total_energy = 0
    rows = grid.shape[0]
    cols = grid.shape[1]

    for x in range(rows):
        for y in range(cols):
            neighbors = get_neighbors(x, y, rows, cols)
            identical_neighbors = count_identical_neighbors(neighbors,
                                                            grid[x][y],
                                                            grid)
            opposite_neighbors = 4 - identical_neighbors
            total_energy += opposite_neighbors
            
    return total_energy


from scipy.constants import physical_constants

#boltzmann constant (units of eV/K) used to calculate probability
k = physical_constants['Boltzmann constant in eV/K'][0]

def calculate_boltzmann_probability(energy1,energy2,temperature):
    """Calculates a boltzmann probability for a hypothetical
    energy difference (`delta_energy`) between `energy1` and
    `energy2` at a certain `temperature` in units of Kelvin.
    """
    delta_energy = ((energy2 - energy1) / 100)
    return np.exp(delta_energy / (k * temperature))


#the doc string for this function was gratiously generated by ChatGPT

def phase_separate(grid,temperature=None,iterations=100000):
    """
    Performs a Monte Carlo simulation to phase separate the input grid.

    Parameters:
    -----------
    grid : numpy.ndarray
        A 2-dimensional numpy array representing the grid to be phase separated.
    temperature : float
        A float representing the temperature for the Monte Carlo simulation.
    iterations : int, optional
        The number of iterations to perform for the Monte Carlo simulation. Default is 100000.

    Returns:
    --------
    numpy.ndarray
        The phase separated grid.
    float
        The total energy of the phase separated grid.
    pandas.DataFrame
        A DataFrame containing the swap records of the Monte Carlo simulation.

    Notes:
    ------
    This function takes a 2-dimensional numpy array as input and performs a Monte Carlo simulation 
    to phase separate the grid. The simulation randomly selects two grid points and checks the neighbors 
    around each point. If there are more identical neighbors for one point at the location of the other point, 
    the values will switch. If the condition isn't true, a Boltzmann probability is calculated and the values 
    switch based on a random number generator. The function returns the total energy of the phase separated grid.
    """
    
    df_rows = []
    
    rows = grid.shape[0]
    cols = grid.shape[1]
    
    for i in range(iterations):
    
        x1,y1 = random_grid_point(grid)
        grid1 = grid[x1][y1]
    
        x2,y2 = random_grid_point(grid)
        grid2 = grid[x2][y2]
    
        neighbors1 = get_neighbors(x1, y1, rows, cols)
        neighbors2 = get_neighbors(x2, y2, rows, cols)
    
        # check if the neighbors around grid point 1 match
        count1 = count_identical_neighbors(neighbors1,grid1,grid)
    
        # check if the neighbors around grid point 2 would match grid point 1
        count2 = count_identical_neighbors(neighbors2,grid1,grid)
            
        # if there are more identical neights for grid point 1 at the location
        # of grid point two, the values will switch
        
        switch = False
        prob = None
        rand = None
    
        if count2 > count1:
            grid[x1][y1] = grid2
            grid[x2][y2] = grid1
            switch = True
        
        else:
            
            if temperature is not None:
                
                prob = calculate_boltzmann_probability(count1, count2, temperature)
                rand = np.random.rand()
        
                if rand < prob:
                    grid[x1][y1] = grid2
                    grid[x2][y2] = grid1
                    switch = True
                    
        total_energy = count_total_energy(grid)
        
        swap_records = [x1,y1,grid1,x2,y2,grid2,count1,count2,prob,rand,switch,total_energy]
        
        df_rows.append(swap_records)
                
    separated_grid = grid
    
    df_swap_records = pd.DataFrame(df_rows,columns=['x1','y1','grid1','x2','y2','grid2',
                                                    'count1','count2','prob','rand',
                                                    'switch','total_energy'])
            
    return separated_grid, total_energy, df_swap_records



