import service_account as acc
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


# Connect to sheets API and retrieve latest sheet
data_sheet = acc.Spreadsheet('Applications', 'Main').sheet

# Convert google sheet to csv for pandas use
rows = data_sheet.get_all_values()
df = pd.DataFrame.from_records(rows)
print(df)

# Init Dash app
app = dash.Dash(__name__)

# Define layout property of app

