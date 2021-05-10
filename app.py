import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sodapy import Socrata

version = "1.0"
client = Socrata("data.ct.gov", None)
results = client.get("28fr-iqnx",limit=50000)
cvd = pd.DataFrame.from_records(results)

data = pd.read_csv('https://data.ct.gov/resource/ncg4-6gkj.csv')
vac_data = pd.read_csv('https://data.ct.gov/resource/tttv-egb7.csv')
data["dateupdated"] = pd.to_datetime(data["dateupdated"], format="%Y-%m-%d")
vac_data['date_updated'] = pd.to_datetime(vac_data["date_updated"], format="%Y-%m-%d")
data.sort_values("dateupdated", inplace=True)
vac_data.sort_values("date_updated", inplace=True)
external_stylesheets =['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Pierrepont COVID-19 Dashboard'

total_vac = vac_data.loc[vac_data['category']=='Total']

cvd["lastupdatedate"] = pd.to_datetime(cvd["lastupdatedate"], format="%Y-%m-%d")
cvd = cvd.sort_values('town')
cvd = cvd.sort_values('lastupdatedate')

def create_card(header, content, colors, change):
    card_content = [
        dbc.CardHeader(header),
        dbc.CardBody(
            [
                html.H5(content, className="card-title"),
                html.P(change, className="card-text"),
            ]
        ),
    ]
    card = dbc.Card(card_content, color=colors, inverse=True)
    return(card)
def sign(chnge):
    if chnge > 0:
        return ('+'+str(chnge))
    elif chnge < 0:
        return ('-'+str(chnge))

card1 = create_card("Cases (Confirmed and Probable)", data.iloc[-1,1], 'primary',str(data.iloc[-1,2])+str(data.iloc[-1,3]))
card2 = create_card("Daily Test Positivity", str(data.iloc[-4,3])+'%','success',str(sign(round(data.iloc[-4,3]-data.iloc[-9,3],2)))+'%')
card3 = create_card("At Least One Dose Vaccinated Percent", str(total_vac.iloc[-1,3])+'%','info', str(sign(round(total_vac.iloc[-1,3]-total_vac.iloc[-2,3],2)))+'%')
card4 = create_card("Hospitalizations", data.iloc[-2,1],'warning',str(data.iloc[-2,2])+str(data.iloc[-2,3]))
card5 = create_card("Deaths", data.iloc[-3,1],'danger',str(data.iloc[-3,2])+str(data.iloc[-3,3]))

graphRow0 = dbc.Row([dbc.Col(id='card1', children=[card1]),
                     dbc.Col(id='card2', children=[card2]), 
                     dbc.Col(id='card3', children=[card3]),
                     dbc.Col(id='card4', children=[card4]),
                     dbc.Col(id='card5', children=[card5])])


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Pierrepont COVID-19 Dashboard", className="header-title"
                ),
            ],
            className="header",
        ),
        html.Div(
            [html.Br(),graphRow0]
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Town", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter",
                            options=[
                                {"label": ct_town, "value": ct_town}
                                for ct_town in np.sort(cvd.town.unique())
                            ],
                            value="Andover",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Cases/Deaths/Caserate", className="menu-title"),
                        dcc.Dropdown(
                            id="case-filter",
                            options=[
                                {"label": c, "value": c.replace(" ", "").lower()}
                                for c in ['Town Total Cases', 'Town Total Deaths', 'Town Case Rate']
                            ],
                            value="towntotalcases",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ]
        ),
        html.Div(
                children=[
                    html.Div(
                        children="Date Range",
                        className="menu-title"
                        ),
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=cvd.lastupdatedate.min().date(),
                        max_date_allowed=cvd.lastupdatedate.max().date(),
                        start_date=cvd.lastupdatedate.min().date(),
                        end_date=cvd.lastupdatedate.max().date(),
                    ),
                ]
        ),
        html.Div(
            children=[
                html.Div(
                    children = "Compare To Another Town",
                    className = "menu-title" 
                    ),
                dcc.RadioItems(
                    id = "radio-items",
                    options=[
                        {'label': 'Yes', 'value': 'Yes'},
                        {'label': 'No', 'value': 'No'},
                    ],
                    value = 'No'
                )
            ]
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Second Town", className="menu-title"),
                        dcc.Dropdown(
                            id="region-filter2",
                            options=[
                                {"label": ct_town, "value": ct_town}
                                for ct_town in np.sort(cvd.town.unique())
                            ],
                            value="Ansonia",
                            clearable=False,
                            className="dropdown",
                            
                        ),
                    ]
                ),
            ], style = {'display': 'block'}
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="cases-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)
@app.callback(
    Output('region-filter2', 'style'),
    [
       Input('radio-items', 'value')
    ],
)
def show_hide_element(visibility_state):
    if visibility_state == 'Yes':
        return html.Div('Yes')
        #return {'display': 'block'}
    if visibility_state == 'No':
        return html.Div('No')
        #return {'display': 'none'}

@app.callback(
    Output("cases-chart", "figure"), #add more outputs for more graphs
    [
        Input("region-filter", "value"),
        Input("case-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("radio-items", "value"),
        Input("region-filter2", "value"),
    ],
)
def update_charts(region, case_value, start_date, end_date, radio, region2):
    if radio == "No": 
        mask = (
            (cvd.town == region)
            & (cvd.lastupdatedate >= start_date)
            & (cvd.lastupdatedate <= end_date)
        )

        filtered_data = cvd.loc[mask, :]
        cases_chart_figure =  make_subplots()

        cases_chart_figure.add_trace(
            go.Scatter(x = filtered_data["lastupdatedate"], y = filtered_data[case_value], name = region),
        )

        if(case_value == 'towntotalcases'):
            cases_chart_figure.update_layout(
                title_text = region + ' Total Covid-19 Cases'
            )
            cases_chart_figure.update_yaxes(title_text = 'Town Total Cases')
        if(case_value == 'towntotaldeaths'):
            cases_chart_figure.update_layout(
                title_text = region + ' Total Covid-19 Deaths'
            )
            cases_chart_figure.update_yaxes(title_text = 'Town Total Deaths')
        if(case_value == 'towncaserate'):
            cases_chart_figure.update_layout(
                title_text = region + ' Covid-19 Case Rate Per 100,000 People'
            )
            cases_chart_figure.update_yaxes(title_text = 'Town Case Rate Per 100k People')

        
        cases_chart_figure.update_xaxes(title_text = "Date Range")
        return cases_chart_figure

    if radio == "Yes":
        mask1 = (
            (cvd.town == region)
            & (cvd.lastupdatedate >= start_date)
            & (cvd.lastupdatedate <= end_date)
        )
        mask2 = (
            (cvd.town == region2)
            & (cvd.lastupdatedate >= start_date)
            & (cvd.lastupdatedate <= end_date)
        )
        filter1 = cvd.loc[mask1, :]
        filter2 = cvd.loc[mask2, :]

        cases_chart_figure2 =  make_subplots()

        cases_chart_figure2.add_trace(
            go.Scatter(x = filter1["lastupdatedate"], y = filter1[case_value], name = region),
        )
        cases_chart_figure2.add_trace(
            go.Scatter(x = filter2["lastupdatedate"], y = filter2[case_value], name = region2),
        )
        if(case_value == 'towntotalcases'):
            cases_chart_figure2.update_layout(
                title_text = region + ' v. ' + region2 +' Total Covid-19 Cases'
            )
            cases_chart_figure2.update_yaxes(title_text = 'Town Total Cases')
        if(case_value == 'towntotaldeaths'):
            cases_chart_figure2.update_layout(
                title_text = region + ' v. ' + region2 + ' Total Covid-19 Deaths'
            )
            cases_chart_figure2.update_yaxes(title_text = 'Town Total Deaths')
        if(case_value == 'towncaserate'):
            cases_chart_figure2.update_layout(
                title_text = region + ' v. ' + region2 + ' Covid-19 Case Rate Per 100,000 People'
            )
            cases_chart_figure2.update_yaxes(title_text = 'Town Case Rate Per 100k People')

        cases_chart_figure2.update_xaxes(title_text = "Date Range")
        return cases_chart_figure2



if __name__ == '__main__':
    app.run_server(debug=True)
