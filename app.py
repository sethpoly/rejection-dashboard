import service_account as acc
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px

# Connect to sheets API and retrieve latest sheet
data = acc.Spreadsheet('Applications', 'Main').sheet

# Convert google sheet to csv for pandas use
rows = data.get_all_records()
df = pd.DataFrame(rows)
df["dateApplied"] = pd.to_datetime(df["dateApplied"], infer_datetime_format=True)

# Drop null values from df
df = df[df.dateApplied.notnull()]

# Init Dash app
app = dash.Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Get data for Apps Sent/Rejection containers
app_count = len(df.index)
rejection_count = df[df["wasRejected"] == 'TRUE'].shape[0]
response_rate = (df[df["initialScreeningRejection"] == 'FALSE'].shape[0] / app_count)  # Calculate response rate
response_rate = "{:.2%}".format(response_rate)  # Convert to percent

fig = px.scatter(df, x=df["dateApplied"].unique(), y=df.groupby(['dateApplied']).size(),
                 size_max=60,
                 labels={
                     "x": "Date Applied",
                     "y": "Applications Sent"
                 },
                 title="Applications Sent Per Day")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

# Define layout property of app
app.layout = html.Div([
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
    # Double boxes with Applications Sent & Rejection data
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
                        children="Response Rate", className="container-title"),
                    html.P(response_rate, className="container-value", style={'color': 'red'})
                ]
            )
        ]
    ),
    html.Div(
        children=[
            dcc.Graph(
                id="apps_per_day_graph",
                figure=fig,
                className="graph-container"
            )
        ]
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
