#!/usr/bin/env python
# coding: utf-8

# In[2]:


from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
from dash.exceptions import PreventUpdate
import json 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets) 

df = px.data.gapminder()

app.layout = html.Div([
    html.H1("Gapminder 互動式儀表板", 
            style={'textAlign': 'center', 'color': '#2C3E50', 'padding': '15px'}),
    
    # 年份滑桿 
    html.Div([
        html.Label('請選擇年份:', style={'fontWeight': 'bold'}),
        dcc.Slider(
            df['year'].min(),
            df['year'].max(),
            step=None,
            id='year-slider',
            value=df['year'].max(), # 預設為最新年份
            marks={str(year): str(year) for year in df['year'].unique()}
        )
    ], style={'width': '95%', 'padding': '0 20px 20px 20px', 'margin': 'auto'}),

    # 區域 : 圖表
    html.Div([
        # (左)散佈圖
        dcc.Graph(id='scatter-plot', 
                  style={'width': '49%', 'display': 'inline-block', 'padding': '0 10px'}),
        
        # (右)旭日圖
        dcc.Graph(id='sunburst-chart', 
                  style={'width': '49%', 'float': 'right', 'display': 'inline-block', 'padding': '0 10px'}),
    ], style={'padding': '10px 0'}),
    
    dcc.Store(id='intermediate-data', storage_type='session')
])

@callback(
    Output('intermediate-data', 'data'),
    Input('year-slider', 'value')
)
def store_data(selected_year):
    """根據選擇的年份篩選數據，並將 DataFrame 轉為 JSON 字符串存儲。"""
    if selected_year is None:
        raise PreventUpdate

    dff = df[df['year'] == selected_year]
    
    return dff.to_json(date_format='iso', orient='split')

# Callback 2: 繪製散佈圖 
@callback(
    Output('scatter-plot', 'figure'),
    Input('intermediate-data', 'data') 
)
def update_scatter_plot(jsonified_filtered_data):
    """從存儲中讀取數據，並繪製散佈圖。"""
    if jsonified_filtered_data is None:
        raise PreventUpdate

    dff = pd.read_json(jsonified_filtered_data, orient='split')

    fig_scatter = px.scatter(
        dff, 
        x="gdpPercap", 
        y="lifeExp", 
        size="pop",
        color="continent",
        hover_name="country",
        log_x=True,
        size_max=60,
        title=f"人均GDP vs. 預期壽命 ({dff['year'].iloc[0]}年)",
        labels={
            "gdpPercap": "人均GDP (對數)", 
            "lifeExp": "預期壽命 (年)",
            "pop": "人口數"
        },
        height=550
    )
    fig_scatter.update_layout(transition_duration=500, margin={'t': 40})
    
    return fig_scatter

# Callback 3: 繪製旭日圖
@callback(
    Output('sunburst-chart', 'figure'),
    Input('intermediate-data', 'data') 
)
def update_sunburst_chart(jsonified_filtered_data):
    """從存儲中讀取數據，並繪製旭日圖。"""
    if jsonified_filtered_data is None:
        raise PreventUpdate

    dff = pd.read_json(jsonified_filtered_data, orient='split')
    
    fig_sunburst = px.sunburst(
        dff, 
        path=['continent', 'country'],
        values='pop',
        color='continent',
        title=f"各大洲與國家人口分佈 ({dff['year'].iloc[0]}年)",
        height=550
    )
    fig_sunburst.update_layout(transition_duration=500, margin={'t': 40})

    return fig_sunburst

if __name__ == '__main__':
    app.run(debug=True)


# In[ ]:




