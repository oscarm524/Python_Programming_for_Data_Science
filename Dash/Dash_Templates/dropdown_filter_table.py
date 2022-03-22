import dash
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
from sklearn.utils import resample

## Reading data 
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
df = df[['continent', 'country', 'pop', 'lifeExp']]  # prune columns for example

def generate_table(dataframe, max_rows = 10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))] 
    )

app = Dash(__name__)


app.layout = html.Div(children = [
    html.H1(children = 'Toy Example'),
    dcc.Dropdown(id = 'dropdown', 
    options = [
        {'label': i, 'value': i} for i in df.continent.unique()
    ], 
    multi = True, 
    placeholder = 'Filter by continent'),
    html.Div(id = 'table-container'), 
    
    html.H1('Summary Statistics of Life Expentancy'),
    html.Div(id = 'summary-stats')
])

@app.callback(
    Output('table-container', 'children'),
    [Input('dropdown', 'value')])
def display_table(dropdown_value):
    if dropdown_value is None:
        return generate_table(df)

    dff = df[df.continent.str.contains('|'.join(dropdown_value))]
    return generate_table(dff)


def bootstrap_ci(values):

    results = list()
    
    for i in range(0, 1000):
        
        results.append(resample(values, replace = True))
    
    return np.std(results, ddof = 1)


@app.callback(
    Output('summary-stats', 'children'),
    [Input('table-container','children')])
def summary_stats(data):
    
    x = data['props']['children']
    numbs = list()
    
    for i in range(1, len(x)): 
        numbs.append(pd.DataFrame(x[i]['props']['children'])['props'][3]['children'])
    
    average = round(np.mean(numbs), 2)
    minimum = round(np.min(numbs), 2)
    maximum = round(np.max(numbs), 2)
    sd = bootstrap_ci(numbs)
    low_bound = round(average - 2*sd, 2)
    up_bound = round(average + 2*sd, 2)
    
    data_out = pd.DataFrame({'Average': average, 'Min': minimum, 'Max': maximum, 'Lower Bound': low_bound, 'Upper Bound': up_bound}, index = [0])
    return generate_table(data_out)
