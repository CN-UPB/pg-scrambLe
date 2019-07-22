import pandas as pd
import numpy as np
from scipy.stats import t # sudo pip3 install scipy

t_bounds = t.interval(0.95, len(data) - 1)

raw_data = {'name': ['Willard Morris', 'Al Jennings', 'Omar Mullins', 'Spencer McDaniel'],
    'age': [20, 19, 22, 21],
    'favorite_color': ['blue', 'red', 'yellow', "green"],
    'grade': [88, 92, 95, 70]}

df = pd.DataFrame(raw_data, index = ['Willard Morris', 'Al Jennings', 'Omar Mullins', 'Spencer McDaniel'])
df