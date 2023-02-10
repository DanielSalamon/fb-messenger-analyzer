import plotly.graph_objects as go

def plot_monthly_messages(df):

    #
    #   Create a line chart of number of messages sent per month
    #   Input: Pandas DataFrame with converted timestamps
    #   Output: Line chart in format of matplotlib figure
    #

    layout = go.Layout(
    paper_bgcolor='lightgrey',#'rgba(0,0,0,0)',
    plot_bgcolor='lightgrey')#'rgba(0,0,0,0)')

    df = df.groupby(['month']).size().reset_index(name='counts')

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']

    fig = go.Figure(layout=layout)

    fig.add_trace(go.Scatter(x=months, y=df["counts"], name='Messages per month', 
                mode="lines+markers+text",text=df['counts'], textposition="top right",
        textfont=dict(
            family="Verdana",
            size=12,
            color="black"
        ), line = dict(color='LightSeaGreen', width=2)))



    fig.update_layout(title='Messages sent in conversation',
                    xaxis_title='Month',
                    yaxis_title='Number of messages sent',
                    font=dict(
            family="Verdana",
            size=12,
            color="DarkBlue"
        )
                    )

    fig.show()


def distribution_pie(df):

    #
    #   Create a pie chart message distribution among conversation participants
    #   Input: Pandas DataFrame with converted timestamps
    #   Output: Pie chart in format of matplotlib figure
    #

    labels = df['sender_name'].unique()
    counts = df['sender_name'].value_counts()
    labels = counts.index

    layout = go.Layout(
        paper_bgcolor='lightgrey',#'rgba(0,0,0,0)',
        plot_bgcolor='lightgrey')#'rgba(0,0,0,0)')


    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Pie(labels=labels, values=counts, hole=.3))


    fig.update_traces(hoverinfo='label+percent', textinfo='label+value+percent', textfont_size=15, textposition='inside')
    fig.update_layout( margin=dict(t=0, b=0, l=0, r=0),
            
                        font=dict(
                family="Verdana",
                size=12,
                color="DarkBlue"
            ), showlegend=False, width=500
                        )
    fig.show()