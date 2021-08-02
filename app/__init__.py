"""Main flask application. Create and display plots."""

from flask import Flask, render_template
import pandas as pd
import json
import plotly
from plotly.subplots import make_subplots
from pathlib import Path

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
    fig = make_subplots(rows=3, cols=2,
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
    fig.add_bar(x=df_time['timestamp'], y=df_time['blitz_api'],
                marker_color=df_status['color'], row=1, col=1,
                text=[status_dic[i] for i in df_status['color']],
                hovertemplate='Time: %{x}<br>' +
                              'Blitz API response time: %{y} ms<br>' +
                              'Status: %{text}' +
                              '<extra></extra>'
                )
    fig.add_bar(x=df_sessions['timestamp'], y=df_sessions['sessions'],
                row=2, col=1,
                hovertemplate='Time: %{x}<br>' +
                              'Total sessions: %{y}<br>' +
                              '<extra></extra>')
    fig.add_bar(x=df_sessions['timestamp'], y=df_sessions['users'],
                row=2, col=2,
                hovertemplate='Time: %{x}<br>' +
                              'Unique users: %{y}<br>' +
                              '<extra></extra>')
    fig.add_bar(x=df_time['timestamp'], y=df_time['webpage'],
                row=3, col=1,
                hovertemplate='Time: %{x}<br>' +
                              'Webpage response time: %{y} ms<br>' +
                              '<extra></extra>')
    fig.add_bar(x=df_time['timestamp'], y=df_time['json_api'],
                row=3, col=2,
                hovertemplate='Time: %{x}<br>' +
                              'JSON API response time: %{y} ms<br>' +
                              '<extra></extra>')
    fig.update_layout(height=1200, showlegend=False)
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


@app.route('/')
def index():
    """Render the HTML template with a plot."""
    folder = "/data"
    bar = create_plot(folder)
    return render_template('index.html', plot=bar)
