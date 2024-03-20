#import dependencies
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import numpy as np
import plotly.express as px

# use pandas to read the csv file that is in the same file directory
df = pd.read_csv("gdp_pcap.csv")
df.head() #display the first five rows of the dataset

#this code cell is for all the preprocessing of the data that is done to ensure that the components are visually enhancing

#use the pd.melt function to reshapes the dataframe into a long table with one row for each each column (will help when making the dash components)
df_long = pd.melt(df, id_vars=['country'], var_name='year', value_name='gdpPercap') 
min_year = int(df_long['year'].min()) #creating the minimum year using the 'melted' version of the data set and the .min() function
max_year = int(df_long['year'].max()) #creating the maximum year using the 'melted' version of the data set and the .max() function
df_long['gdpPercap'] = pd.to_numeric(df_long['gdpPercap'], errors='coerce') #convert the gdp into a numeric value (used errors = 'coerce' through a stack overflow thread)
df_long_sorted = df_long.sort_values(by=['year','gdpPercap']) #sort the values by year and gdpPercap which will be used will for the graph below
y_ticks = list(range(0, int(df_long_sorted['gdpPercap'].max()) + 1000, 1000)) #sets a new variable for the y-axis (this gets rid of the "k" and allows for constant increments)
x_ticks = list(range(min_year, max_year + 1, 25)) #sets a new variable for the x-axis (this allows for constant increments and sorts the x-axis by 50 years)
df_long.head() #displays the dataset to see if I implemented the pd.melt command properly

stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # loading the CSS stylesheet (referenced the class6 material)

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app using the stylesheet for stylistic features

import dash
app.layout = html.Div([ #parent div
    html.Div(style={'textAlign': 'center'}, children=[ #creates another div for the heading (text align indicates that the heading is in the center)
    html.H1("GDP per Capita Analysis")
    ]),

    #app description is below
    html.P("The app leverages the extensive Gapminder dataset, which encompasses a comprehensive collection of economic indicators, including but not limited to the Gross Domestic Product (GDP) of most countries. GDP serves as the cornerstone metric for evaluating the monetary worth of all final goods and services produced within a nation's borders over a specific period. This dashboard presents users with a dropdown menu featuring an array of countries, enabling the selection of multiple nations for comparative analysis. Additionally, a slider grants users the flexibility to choose a range of years, facilitating longitudinal examination of GDP trends. The graphical representation adjusts based on the dropdown and slider components. Overall, this design choice enhances user comprehension and facilitates easy interpretation of complex data sets. As a result, users can effortlessly explore and analyze GDP variations across different countries and timeframes."),

    html.Div(className='row', children=[ #another div for the drop down component
        html.Div(className='six columns', style = {'padding': '10px'},children=[ # className = 'six columns' allows for the components to be split; uses style components for padding and layout purposes
            dcc.Dropdown(
                id='multiple-country-dropdown', #creates the dropdown id
                options=[{'label': country, 'value': country} for country in df['country'].unique()], #creates a function to go through the unique countries so that countries aren't duplicated
                multi=True, #allows for multi select components
                value=["Select..."],  # default statement
                style={'text-align': 'center',
                       'color': 'black',
                       'backgroundColor': 'white'}, #stylistic choices using the style command
            )
        ]),

        html.Div(className='six columns', style = {'padding': '10px'}, children=[ #className = 'six columns' allows for the components to be split; uses style components for padding and layout purposes
            dcc.RangeSlider(
                id = 'year-range-slider', # creates range id
                min = min_year, #uses the min year variable from above for the min value of the slider
                max = max_year, #uses the max year variable from above for the max value of the slider
                marks = {str(year): str(year) for year in range(int(min_year), int(max_year + 1), 50)}, #uses a function to create marks between every 50 years for readability
                value = [min_year, max_year], # when the app is first loaded, the slider handles will be positioned at the beginning and end of the range for easy visualization
            )
        ]),
    ]),
    html.Div(style={'padding': '50px'}, children=[ #allows the graph to be BELOW the other components and take up the whole width of the screen
    dcc.Graph(
        id='gdp-percap-graph', #creates the graph id
        figure=px.line(df_long_sorted, #uses the 'melted' version of the dataset
                       x='year', #x axis is the year 
                       y='gdpPercap', #y axis is the gdp 
                       color='country', #color code based on the country
                       title='GDP vs. Years'
                      ).update_xaxes(tickvals=x_ticks, ticktext=[f"{val}" for val in x_ticks]).update_yaxes(tickvals=y_ticks, ticktext=[f"{val}" for val in y_ticks]) # Update x-axis and y-axis ticks
    ),
])
])

#callback function to update the graph based on the dropdown and range slider
@app.callback(
    Output('gdp-percap-graph', 'figure'),  #the output is the graph
    [Input('multiple-country-dropdown', 'value'),  #the first input is the dropdown
     Input('year-range-slider', 'value')])  #the second input is the range slider
def update_graph(selected_countries, selected_years):
    #filter the dataset based on the selected countries and years
    df_filtered = df_long[(df_long['country'].isin(selected_countries)) &
                          (df_long['year'] >= str(selected_years[0])) &
                          (df_long['year'] <= str(selected_years[1]))] #filter the dataset based on the selected countries and years
    
    #sort the filtered dataset
    df_filtered_sorted = df_filtered.sort_values(by=['year', 'gdpPercap'])
    
    #create the figure
    fig = px.line(df_filtered_sorted,
                  x='year', #year is the x-axis
                  y='gdpPercap', #gdp is the y-axis
                  color='country',
                  title='GDP per Capita throughout the Years in Various Countries').update_xaxes(tickvals=x_ticks, ticktext=[f"{val}" for val in x_ticks]).update_yaxes(tickvals=y_ticks, ticktext=[f"{val}" for val in y_ticks]) # the update x-axis and y-axis ticks
    
    return fig #display new figure

server = app.server

if __name__ == '__main__':
    server.run(debug=False)
