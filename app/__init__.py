"""Main flask application. Create and display plots."""

from flask import Flask, render_template
import pandas as pd
import json
import plotly
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime, timedelta

app = Flask(__name__)


def get_dataframe(filename):
    """Retrieve a Pandas dataframe from a csv."""
    with open(filename, 'r') as file:
        df = pd.read_csv(file)
        return df


def create_plot(folder):
    """Generate the multiplot to be displayed."""
    df_time = get_dataframe(Path(folder) / 'timings.csv')
    df_status = get_dataframe(Path(folder) / 'status.csv')
    df_sessions = get_dataframe(Path(folder) / 'sessions.csv')
    lastmonth = datetime.today() - timedelta(weeks=2)
    df_time['timestamp'] = pd.to_datetime(df_time['timestamp'])
    df_status['timestamp'] = pd.to_datetime(df_status['timestamp'])
    df_sessions['timestamp'] = pd.to_datetime(df_sessions['timestamp'])
    display_time = df_time[df_time['timestamp']>lastmonth]
    display_status = df_status[df_status['timestamp']>lastmonth]
    display_sessions = df_sessions[df_sessions['timestamp']>lastmonth]
    fig = make_subplots(
        rows=3, cols=2,
        specs=[[{'colspan': 2}, None], [{}, {}], [{}, {}]],
        subplot_titles=("OMERO status and Blitz API response time",
                        "Sessions per day",
                        "Unique users per day",
                        "Web response time",
                        "JSON API response time"),
        horizontal_spacing=0.03, vertical_spacing=0.1,
                        )
    status_dic = {'green': "All systems operational",
                  'orange': "At least one API/service unresponsive",
                  'red': "All systems unresponsive"}
    fig.add_bar(x=display_time['timestamp'], y=display_time['blitz_api'],
                marker_color=display_status['color'], row=1,
                col=1, width=60*50*1000,
                text=[status_dic[i] for i in display_status['color']],
                hovertemplate='Time: %{x}<br>' +
                              'Blitz API response time: %{y} s<br>' +
                              'Status: %{text}' +
                              '<extra></extra>'
                )
    fig.add_bar(x=display_sessions['timestamp'], y=display_sessions['sessions'],
                row=2, col=1, width=60*50*1000*24,
                hovertemplate='Time: %{x}<br>' +
                              'Total sessions: %{y}<br>' +
                              '<extra></extra>')
    fig.add_bar(x=display_sessions['timestamp'], y=display_sessions['users'],
                row=2, col=2, width=60*50*1000*24,
                hovertemplate='Time: %{x}<br>' +
                              'Unique users: %{y}<br>' +
                              '<extra></extra>')
    fig.add_bar(x=display_time['timestamp'], y=display_time['webpage'],
                row=3, col=1, width=60*50*1000,
                hovertemplate='Time: %{x}<br>' +
                              'Webpage response time: %{y} s<br>' +
                              '<extra></extra>')
    fig.add_bar(x=display_time['timestamp'], y=display_time['json_api'],
                row=3, col=2, width=60*50*1000,
                hovertemplate='Time: %{x}<br>' +
                              'JSON API response time: %{y} s<br>' +
                              '<extra></extra>')
    fig.update_xaxes(range=[lastmonth, datetime.now()])
    fig.update_layout(height=1200, showlegend=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/')
def index():
    """Render the HTML template with a plot."""
    folder = "/data"
    bar = create_plot(folder)
    return render_template('index.html', plot=bar)
