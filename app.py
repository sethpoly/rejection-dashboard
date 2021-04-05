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

# Init Dash app
app = dash.Dash(__name__)

fig = px.scatter(df, x=df["dateApplied"].unique(), y=df.groupby(['dateApplied']).size(),
                 size_max=60,
                 labels={
                     "x": "Date Applied",
                     "y": "Applications Sent"
                 },
                 title="Applications Sent Per Day")

# Define layout property of app
app.layout = html.Div(
    children=[
        html.H1(children="Rejection Analytics", ),
        html.P(
            children="Analyze the responses of every job I've ever applied to",
        ),
        dcc.Graph(
            figure=fig
        )
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
