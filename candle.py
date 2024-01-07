from plotly.subplots import make_subplots
import plotly.graph_objs as go

# create a candle template for candle graph
def candle_figure(asset, selected_df='ITUB4.SA'):
    fig = make_subplots(rows = 2, cols = 1, shared_xaxes= True, vertical_spacing=0.05, 
                        row_width= [0.2, 0.7])

    fig.add_trace(go.Candlestick(
        x=asset.index,
        name='Candle',
        open=asset['Open'],
        high=asset['High'],
        low=asset['Low'],
        close=asset['Close']) , row=1, col=1)

    fig.add_trace(go.Scatter(x=asset.index, y=asset['MME15'], name='MME15', marker_color='rgba(0, 128, 255, 0.5)' ))

    fig.update_layout(
        template='plotly_white',
        yaxis1=dict(title='Prices', tickformat=',.2f', tickprefix='R$', fixedrange=True),
        yaxis2=dict(title='Volume', fixedrange=True ),
        xaxis=dict(showgrid=False),
        height=700,
        title_text=f'{selected_df} CandleStick Analysis',
    )
    fig.add_trace(go.Bar(
        marker_color='rgb(99, 110, 250)',
        x = asset.index,
        y = asset['Volume'],
        name='Volume',
        showlegend=False,
    ), row=2, col=1) 

    fig.update(layout_xaxis_rangeslider_visible=False)
    
    return fig
    