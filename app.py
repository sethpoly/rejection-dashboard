import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
from dash.dependencies import Output, Input
import plotly.graph_objects as go
import service_account as acc

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
df.sort_values(by="daysSinceRejection", inplace=True)  # Sort rejection dates by how many days since last rejection

# Data frame for most recent rejections
df_recent_rejects = df[
    (df["wasRejected"] == 'TRUE') & (df['daysSinceRejection'] >= 0) & (df['daysSinceRejection'] < 10)]

colors = {
    'background': '#1f1f1f',
    'text': '#FFF'
}


# Updates visual layout properties of graphs - KEEP CONSISTENT
def update_layout(graph):
    graph.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        xaxis={'fixedrange': True},
        yaxis={'fixedrange': True},
        dragmode=False
    )


# Get data for Apps Sent/Rejection containers
app_count = len(df.index)
rejection_count = df[df["wasRejected"] == 'TRUE'].shape[0]
response_rate = (df[df["initialScreeningRejection"] == 'FALSE'].shape[0] / app_count)  # Calculate response rate
response_rate = "{:.2%}".format(response_rate)  # Convert to percent
first_rounds = df[df["initialScreeningRejection"] == 'FALSE'].shape[0] # Initial resume screen passing count

# Sort rejection dates by date
df.sort_values(by="dateApplied", inplace=True)

# Applications sent per day Line graph
fig = px.line(df, x=df["dateApplied"].unique(), y=df.groupby(['dateApplied']).size(),
              labels={
                  "x": "Date Applied",
                  "y": "Applications Per Day"
              },
              title="Applications Sent Per Day")


# Bar chart with job portals
portal_names = df['applicationPortal'].unique()
portal_names.sort()
fig_pie = px.pie(df, values=df.groupby(['applicationPortal']).size(), names=portal_names
                 , title="Job Boards Used")

# Ratio vars for coverletters
total_screening_clears = df[df["initialScreeningRejection"] == 'FALSE'].shape[0]
coverletter_total = df[df["withCoverLetter"] == 'TRUE'].shape[0]
no_coverletter_total = df[df["withCoverLetter"] == 'FALSE'].shape[0]

# Bar chart for correlation between Coverletter/Rejections
df_passed_screening = df[df["initialScreeningRejection"] == 'FALSE']
dfg = df_passed_screening.groupby('withCoverLetter').count().reset_index()

fig_bar = px.bar(dfg, x="withCoverLetter", y='initialScreeningRejection', color="withCoverLetter",
                 title="Applications With Cover Letter",
                 labels={
                     "withCoverLetter": "Cover Letter Attached",
                     "initialScreeningRejection": "Interviews Received"
                 })

# Bullet graph to show correlation between total cover letters attached to interviews received
# Percent of interviews received from applications sent with a cover letter
letter_correlation = (df_passed_screening[df_passed_screening["withCoverLetter"] == 'TRUE'].shape[
                          0] / coverletter_total) * 100
# Percent of interviews received from applications without a cover letter
letter_correlation_noletter = (df_passed_screening[df_passed_screening["withCoverLetter"] == 'FALSE'].shape[
                                   0] / no_coverletter_total) * 100


# Function to create a bullet graph instance
def create_bullet(value, mode, max_range, title, reference):
    return go.Figure(go.Indicator(
        mode=mode, value=
        value,
        gauge={'axis': {'range': [None, max_range]}},
        number={'suffix': "%"},
        domain={"x": [0.1, 1], 'y': [0, 1]},
        title={
            'text': f"<span style='width:90%;margin: 0 auto;text-align:center;font-size:16px'><b>{title}</b></span>"},
        delta={'reference': reference, 'relative': True}
    ))


# Bullet figure for correlation btwn interviews and applications with a cover letter
fig_bullet = create_bullet(letter_correlation, 'number+delta+gauge', coverletter_total,
                           'Interview Rate With Cover Letter', letter_correlation_noletter)

# Bullet figure for correlation btwn interviews and applications with NO cover letter
fig_bullet_no_letter = create_bullet(letter_correlation_noletter, 'number+delta+gauge', no_coverletter_total,
                                     'Interview Rate Without Cover Letter', letter_correlation)

# Set visual layout for all graphs
update_layout(fig)
update_layout(fig_pie)
update_layout(fig_bar)
update_layout(fig_bullet)
update_layout(fig_bullet_no_letter)

# Sort rejection dates by how many days since last rejection - FOR DATA TABLE
df.sort_values(by="daysSinceRejection", inplace=True)


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
                            children="Analyze data about my applications, responses, and interviews.",
                            className="sub-title"
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
                        ),
                        html.Div(
                            className="container",
                            children=[
                                html.H3(
                                    children="First Round Interviews", className="container-title"),
                                html.P(first_rounds, className="container-value")
                            ]
                        )
                    ]
                ),
                # Start of graphs ------------------------------------------------------------------
                html.Div(
                    className="graph-cards",
                    children=[
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="apps_per_day_graph",
                                    figure=fig,
                                    className="graph-div",
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
                                    value='initialScreeningRejection',
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
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="cover_bullet",
                                    figure=fig_bullet,
                                    className="graph-div"
                                )
                            ]
                        ),
                        html.Div(
                            children=[
                                dcc.Graph(
                                    id="no_cover_bullet",
                                    figure=fig_bullet_no_letter,
                                    className="graph-div"
                                )
                            ]
                        )
                    ]
                )
            ]),
        # End of graphs ------------------------------------------------------------------------
        html.Div(
            className='table-div',
            children=[
                html.H1(className="data-header", children="Recent Rejections"),
                dash_table.DataTable(
                    id='reject_table',
                    data=df_recent_rejects.to_dict('records'),
                    columns=[
                        {"name": "Company", "id": "Company"},
                        {"name": 'Date', "id": 'dateRejected'},
                        {"name": "# Days To Respond", "id": "daysUnanswered"}
                    ],
                    style_as_list_view=True,
                    style_header={'backgroundColor': 'rgb(10, 10, 10)',
                                  'border': 'none'},
                    style_data={
                        'border': '1px solid gray'
                    },
                    style_cell={
                        'backgroundColor': '#1f1f1f',
                        'color': 'white',
                        'textAlign': 'center',
                        'font-size': '12px'
                    }
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
app.title = 'Rejection Dashboard'


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

    update_layout(chart)

    return chart


if __name__ == "__main__":
    app.run_server(debug=True)
