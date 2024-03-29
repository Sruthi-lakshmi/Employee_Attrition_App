import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, dash_table, callback, Input, Output, State

df = pd.read_csv("employee_attrition.csv")

def variable_table(dataframe, variable, target_variable): 
    table = pd.crosstab(index=dataframe[variable], columns=dataframe[target_variable], margins=True)
    table.columns = ['Attrition_No', 'Attrition_Yes', 'Grand_Total_Count']
    table['No_Percent'] = (table['Attrition_No'] / table['Grand_Total_Count'] * 100).round(2).astype(str) + '%'
    table['Yes_Percent'] = (table['Attrition_Yes'] / table['Grand_Total_Count'] * 100).round(2).astype(str) + '%'
    table['Grand_Total_Percent'] = ((table['Attrition_No'] + table['Attrition_Yes']) / table['Grand_Total_Count'] * 100).round(2).astype(str) + '%'
    table.index.name = f"{variable}"
    table.reset_index(inplace=True)  
    return table

def stacked_bar_chart(table, table_name,categories):
    table = table.copy()
    table[['No_Percent', 'Yes_Percent']] = table[['No_Percent', 'Yes_Percent']].replace('%', '', regex=True).astype(float)

    fig = px.bar(table, x=categories, y=['No_Percent', 'Yes_Percent'], barmode='stack', color_discrete_sequence=['#0096FF', '#50C878'])
    for index, row in table.iterrows():
        fig.add_annotation(x=index, y=row['No_Percent'] / 2, text=f"{row['Attrition_No']}({row['No_Percent']}%)", font=dict(color='white', size=10),showarrow=False)
        fig.add_annotation(x=index, y=row['No_Percent'] + row['Yes_Percent'] / 2,text=f"{row['Attrition_Yes']}({row['Yes_Percent']}%)", font=dict(color='white', size=10),showarrow=False)
    fig.update_layout(title=f'{table_name} vs Attrition', title_x=0.5, xaxis_title='Categories', yaxis_title='Value')
    return fig

def barchart(table,table_name,categories):

    table = table.copy()
    total_counts = table['Grand_Total_Count'].sum()
    table['Percentage'] = (table['Grand_Total_Count'] / total_counts) * 100
    fig = px.bar(table,x=categories,y='Grand_Total_Count',color_discrete_sequence=["#0096FF"])
    for i, row in table.iterrows():
        fig.add_annotation(x=i, y=row['Grand_Total_Count']/2, text=f'{row["Grand_Total_Count"]}({row["Percentage"]:.2f}%)', showarrow=False,font=dict(color='white', size=12))
    fig.update_layout(title=f'{table_name}', title_x=0.5, xaxis_title='Categories')
    return fig

variables = df.columns.tolist()

app = Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(src="static\image.png",alt="Logo",style={'width':'50%','display': 'block', 'margin': 'auto','vertical-align': 'middle'})
        ],width={'size': 4}),

        dbc.Col([html.H1("Employee Attrition Analysis Report",className='mb-2')])
        ],align='center'),

    dbc.Row([
        dbc.Col([
            html.Label('Click the Radio Buttons',style={'font':25,'fontWeight': 'normal','text-align': 'center'}),
            dcc.RadioItems(id='radio',options= ['Univariate','Bivariate'],value='Bivariate', style={'color': 'Black', 'font-size': 25,'gap':'20x','padding-left': 10,'text-align': 'center'},
                            labelStyle={"display": "inline-block", "align-items": "center"},className='me-2 mb-2 border border-grey')],
            width={'size': 4,'offset':1},align='center'),
            
        dbc.Col([
            html.Label('Select from the dropdown list',style={'font':25,'fontWeight': 'normal','color':'Black'}),
            dcc.Dropdown(id='dropdown',options=[{'label': i, 'value': i} for i in variables],value = "Age_Group",searchable=True,clearable=True,placeholder="Please Select...",style={'width':'100%','color': 'Black'},className='mb-2'),
            dbc.Button('Apply',color='primary',id ='button',outline=True,className='mb-4')],width={'size':6}),
            dbc.Spinner(html.Div(id="loading-output"))]),

    dbc.Row([
        dbc.Col([
            html.Div(id="button-updated"),
            html.Div(id='output', children='Table and Chart')
        ])
    ])
])

@app.callback(
    Output(component_id='output', component_property='children'),
    [Input(component_id='button', component_property='n_clicks')],
    [State(component_id='radio', component_property='value'),
     State(component_id='dropdown', component_property='value')]
)
def update_output(n_clicks, radio_selected, selected_variable):
    if n_clicks is None:
        return ''
    html.Div([html.Label(f"Table and Chart {selected_variable}")])
    table = variable_table(df, selected_variable, 'Attrition')
    table = table[table[selected_variable] != "All"]
    categories = table[selected_variable].tolist()
   
    if radio_selected == "Bivariate":
        bivariate = stacked_bar_chart(table, selected_variable, categories)
        output = html.Div([
            dash_table.DataTable(
                data=table.to_dict('records'),
                columns=[{"name": i, "id": i} for i in table.columns], id='table',style_cell={'padding': '5px'},
                style_header={'backgroundColor': '#C4E4FF','fontWeight': 'bold'}),
            dcc.Graph(id='barchart', figure=bivariate)])
    else:
        if radio_selected == "Univariate":
            univariate = barchart(table, selected_variable, categories)
            output = html.Div([
                dash_table.DataTable(
                    data=table.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in table.columns], id='table',
                    style_header={'backgroundColor': '#C4E4FF','fontWeight': 'bold','border': '1px black'},
                    style_cell={'padding': '5px'}),
                dcc.Graph(id='barchart', figure=univariate)])
    return output

if __name__ == '__main__':
    app.run_server(debug=True,port=8051)
