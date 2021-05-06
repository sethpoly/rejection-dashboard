import service_account as acc
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input
from datetime import datetime

# Init Dash app
app = dash.Dash(__name__,
                meta_tags=
                [{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

# Connect to sheets API and retrieve latest sheet
data = acc.Spreadsheet('Applications', 'Main').sheet

# Convert google sheet to csv for pandas use
rows = data.get_all_records()
df = pd.DataFrame(rows)
df["dateApplied"] = pd.to_datetime(df["dateApplied"], infer_datetime_format=True)

# Drop null values from df
df = df[df.dateApplied.notnull()]

# Data frame for most recent rejections
df_recent_rejects = df[(df["wasRejected"] == 'TRUE') & (df['daysSinceRejection'] > 0) & (df['daysSinceRejection'] < 10)]
df_recent_rejects.sort_values(by="daysSinceRejection", inplace=True)
print(df_recent_rejects.head())

colors = {
    'background': '#1f1f1f',
    'text': '#FFF'
}

# Get data for Apps Sent/Rejection containers
app_count = len(df.index)
rejection_count = df[df["wasRejected"] == 'TRUE'].shape[0]
response_rate = (df[df["initialScreeningRejection"] == 'FALSE'].shape[0] / app_count)  # Calculate response rate
response_rate = "{:.2%}".format(response_rate)  # Convert to percent

fig = px.line(df, x=df["dateApplied"].unique(), y=df.groupby(['dateApplied']).size(),
                 labels={
                     "x": "Date Applied",
                     "y": "Applications Per Day"
                 },
                 title="Applications Sent Per Day")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

# Pie chart with job portals
portal_names = df['applicationPortal'].unique()
portal_names.sort()
fig_pie = px.pie(df, values=df.groupby(['applicationPortal']).size(), names=portal_names
                 , title="Job Boards Used")

fig_pie.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

# Bar chart for correlation between Coverletter/Rejections
#
# total_screening_clears = df[df["initialScreeningRejection"] == 'FALSE'].shape[0]
# coverletter_total = df[df["withCoverLetter"] == 'TRUE'].shape[0]
# coverletter_true = df_coverletter[df["withCoverLetter"] == 'TRUE'].shape[0]
# print(f'Total apps sent with cover letters: {coverletter_total}')
# print(f'With cover letter & passed screening: {coverletter_true}')

df_passed_screening = df[df["initialScreeningRejection"] == 'FALSE']
dfg = df_passed_screening.groupby('withCoverLetter').count().reset_index()
# coverletter_ratio = df_coverletter.shape[0] / df[df["withCoverLetter"] == 'TRUE'].shape[0]
# print(f'Cover letter Ratio: {coverletter_ratio}')
fig_bar = px.bar(dfg, x="withCoverLetter", y='initialScreeningRejection', color="withCoverLetter",
                 title="Applications With Cover Letter",
                 labels={
                     "withCoverLetter": "Cover Letter Attached",
                     "initialScreeningRejection": "Interviews Received"
                 })
fig_bar.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)


# Define layout property of app
def serve_layout():
    return html.Div([
        html.Div(
            className="header-div",
            children=[
                html.Div(
                    className="app-header",
                    children=[
                        html.H1(
                            children="JOB REJECTION DASHBOARD", className="title"),
                        html.H3(
                            children="Analyze the responses of every job I've applied to", className="sub-title"
                        )

                    ]
                ),
                html.Button(id="refresh-btn", n_clicks=0)]
        ),
        # Boxes with Applications Sent & Rejection data
        html.Div(
            className="dashboard-container",
            children=[
                html.Div(
                    className="container-div",
                    children=[
                        html.Div(
                            className="container",
                            children=[
                                html.H3(
                                    children="Applications Sent", className="container-title"),
                                html.P(app_count, className="container-value")
                            ]
                        ),
                        html.Div(
                            className="container",
                            children=[
                                html.H3(
                                    children="Rejections Received", className="container-title"),
                                html.P(rejection_count, className="container-value", style={'color': 'red'})
                            ]
                        ),
                        html.Div(
                            className="container",
                            children=[
                                html.H3(
                                    children="Interview Rate", className="container-title"),
                                html.P(response_rate, className="container-value", style={'color': 'red'})
                            ]
                        )
                    ]

                ),
                html.Div(
                    className="graph-cards",
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="apps_per_day_graph",
                                    figure=fig,
                                    className="graph-div"
                                ),
                            ]
                        ),
                        html.Div(
                            className="graph-div",
                            children=[
                                dcc.Dropdown(
                                    id="coverletter_dropdown",
                                    options=[{'label': 'Interviews Received', 'value': 'initialScreeningRejection'},
                                             {'label': 'Applications Sent', 'value': 'applicationPortal'}],
                                    value='applicationPortal',
                                    clearable=False,
                                ),
                                dcc.Graph(
                                    id="new_bar"
                                )
                            ]

                        ),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="rejection_bar",
                                    figure=fig_bar,
                                    className="graph-div"
                                )
                            ]
                        )
                    ]
                )

            ]),
        html.Div(
            className='table-div',
            children=[
                html.H1(className="data-header", children="Recent Rejections"),
                dash_table.DataTable(
                    id='reject_table',
                    data=df_recent_rejects.to_dict('records'),
                    columns=[
                        {"name": "Company", "id": "Company"},
                        {"name": 'dateRejected', "id": 'dateRejected'},
                        {"name": "withCoverLetter", "id": "withCoverLetter"}
                    ],
                    style_as_list_view=True,
                    style_header={'backgroundColor': 'rgb(30, 30, 30)',
                                  'border': '1px solid gray'},
                    style_data={
                        'border': '1px solid gray'
                    },
                    style_cell={
                        'backgroundColor': '#1f1f1f',
                        'color': 'white'

                    },
                    editable=False
                )]),

        # Contact page at bottom of page
        html.Div(
            className="div-contact",
            children=[
                html.H3(className="copyright-title", children="Seth Polyniak\u00A9 2021"),
                html.Ul(className="social-list", children=[
                    html.A("//Github", className="social-link", href="https://github.com/sethpoly", target="_blank"),
                    html.A("//LinkedIn", className="social-link", href="https://www.linkedin.com/in/sethpolyniak/",
                           target="_blank"),
                    html.A("//Portfolio", className="social-link", href="https://sethpoly.com", target="_blank")
                ])
            ]
        )
    ])


app.layout = serve_layout


# Callback for job board dropdown
@app.callback(
    Output('new_bar', 'figure'),
    Input('coverletter_dropdown', 'value')
)
def build_graph(coverletter_dropdown):  # Param refers to inputs
    dff = df  # Make a copy of df CRUD reasons

    if coverletter_dropdown == "applicationPortal":
        chart = px.bar(
            dff, x=dff.groupby([coverletter_dropdown]).size(), y=portal_names, color=portal_names,
            title="Job Boards Used",
            labels={
                'x': "Applications Sent",
                'y': 'Job Board',
                'color': ''
            }
        )
    elif coverletter_dropdown == "initialScreeningRejection":
        chart = px.bar(
            dff, x=df_passed_screening.groupby('applicationPortal').size(), y=portal_names, color=portal_names,
            title="Job Boards Used",
            labels={
                'x': "Interviews Received",
                'y': 'Job Board',
                'color': ''
            })

    chart.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    return chart


if __name__ == "__main__":
    app.run_server(debug=True)
