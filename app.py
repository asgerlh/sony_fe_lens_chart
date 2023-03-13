from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.express as px
import pandas as pd
import numpy as np
from numerize.numerize import numerize

eps = 0.0001

load_figure_template(['darkly'])

file = 'Sony FE lens list by phillipreeve.net cleaned.xlsx'
df1 = pd.read_excel(file, sheet_name='All')
df2 = pd.read_excel(file, sheet_name='no exif')

df1['Exif'] = 'Yes'
df2['Exif'] = 'No'

df1 = df1.rename(columns={
    'Price \n(please check \nfor actual)': 'Price',
})
df2 = df2.rename(columns={
    'Price \n(please check \nfor current)': 'Price',
})

df2['Price'] = df2['Price'].astype(float)

df = pd.concat((df1, df2))

df = df.rename(columns={
    'Focal\nLength': 'Focal Length',
    'Speed': 'Aperture',
    'Front Filter \nDiameter': 'Filter Diameter',
    'Close\nFocusing\nDistance ': 'Close Focusing Distance',
    'optical \nstabilizer': 'Optical Stabilizer',
    'Aperture\nBlades': 'Aperture Blades',
    'Elements/\nGroups': 'Elements & Groups',
    'Price \n(please check \nfor actual)': 'Price',
    'Used price\n (average \nauction 7/20)': 'Used price',
    'Comment, \nResources': 'Comments',
    'Price \n(please check \nfor current)': 'Price',
})

df.loc[df['Filter Diameter'] == 'na', 'Filter Diameter'] = np.nan

def str2list(d):
    if isinstance(d, str):
        d = [float(f) for f in d.split('-')]
    return d

def focal_length_and_speed_as_list(d):
    f = np.atleast_1d(str2list(d['Focal Length']))
    a = np.atleast_1d(str2list(d['Aperture']))

    if a.shape[-1] < f.shape[-1]:
        a = np.repeat(a, f.shape[-1])

    d['Focal Length'] = f
    d['Aperture'] = a
    return d

df = df.apply(focal_length_and_speed_as_list, axis=1)

df = df.sort_values(by='Weight', ascending=False)

colors = {m: c for m, c in zip(df['Manufacturer'].unique(), px.colors.qualitative.Light24)}

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY, dbc_css])
app.title = 'Sony FE Lens Chart'

def RangeSliderLog(min, max, marks, id, mark_formatter = None):
    if mark_formatter == None:
        mark_formatter = lambda x : str(x)
    r = np.log2(max - min)
    min = np.log2(min) - 0.01*r
    max = np.log2(max) + 0.01*r
    return dcc.RangeSlider(
        min=min,
        max=max,
        value=[min, max],
        marks={int(np.log2(m)) if np.log2(m) % 1 == 0 else np.log2(m): mark_formatter(m) for m in marks},
        step=0.01,
        id=id,
        className='dbc',
    )

controls = dbc.Card([
    dbc.CardHeader([
        html.H1('Sony FE Lens Chart', style={'font-size': '150%', 'margin-bottom': '2px'}),
        html.Div('Size indicates weight'),
    ], style={'text-align': 'center'}),
    dbc.CardBody([
        dbc.Label('Manufacturer', style={'margin-bottom': '1px'}),
        dcc.Dropdown(
            np.sort(df.Manufacturer.unique()),
            [],
            multi=True,
            id='manufacturer',
            className='dbc',
        ),
        dbc.Row([
                dbc.Col([
                dbc.Label('Type', style={'margin-bottom': '1px', 'margin-top': '5px'}),
                dcc.Dropdown(
                    ['Prime', 'Zoom'],
                    None,
                    id='prime-vs-zoom',
                    className='dbc',
                )
            ]),
            dbc.Col([
                dbc.Label('Focus', style={'margin-bottom': '1px', 'margin-top': '5px'}),
                dcc.Dropdown(
                    ['AF', 'MF'],
                    None,
                    id='focus',
                    className='dbc',
                )
            ]),
            dbc.Col([
                dbc.Label('Exif', style={'margin-bottom': '1px', 'margin-top': '5px'}),
                dcc.Dropdown(
                    ['Yes', 'No'],
                    None,
                    id='exif',
                    className='dbc',
                )
            ])
        ]),
        dbc.Label('Focal Length', style={'margin-bottom': '1px', 'margin-top': '5px'}),
        RangeSliderLog(
            df['Focal Length'].apply(lambda fl: fl.min()).min(),
            df['Focal Length'].apply(lambda fl: fl.max()).max(),
            marks=[12, 24, 50, 100, 200, 400],
            id='focal-slider',
            mark_formatter=lambda f : f'{f}mm',
        ),
        dbc.Label('Aperture', style={'margin-bottom': '1px', 'margin-top': '5px'}),
        RangeSliderLog(
            df['Aperture'].apply(lambda fl: fl.min()).min(),
            df['Aperture'].apply(lambda fl: fl.max()).max(),
            marks=[1, 1.4, 2, 2.8, 4, 5.6, 8, 11, 16],
            id='aperture-slider',
            mark_formatter=lambda a : f'f/{a}',
        ),
        dbc.Label('Weight', style={'margin-bottom': '1px', 'margin-top': '5px'}),
        RangeSliderLog(
            df['Weight'].min(),
            df['Weight'].max(),
            marks=[100, 200, 500, 1000, 2000],
            id='weight-slider',
            mark_formatter=lambda x : f"{numerize(x).replace('K', 'k')}g",
        ),
        dbc.Label('Magnification', style={'margin-bottom': '1px', 'margin-top': '5px'}),
        RangeSliderLog(
            df['Magnification'].min(),
            df['Magnification'].max(),
            marks=[0.05, 0.1, 0.2, 0.5, 1, 2, 5],
            id='magnification-slider',
            mark_formatter=lambda x : f'{x}x',
        ),
        dbc.Label('Price', style={'margin-bottom': '1px', 'margin-top': '5px'}),
        RangeSliderLog(
            df['Price'].min(),
            df['Price'].max(),
            marks=[100, 200, 500, 1000, 2000, 5000, 10000],
            id='price-slider',
            mark_formatter=lambda x : f'${numerize(x)}',
        ),
        dbc.Label('Filter Diameter [mm]', style={'margin-bottom': '1px', 'margin-top': '5px'}),
        dcc.Dropdown(
            np.sort(df['Filter Diameter'].unique()),
            [],
            multi=True,
            id='filter',
            className='dbc',
        ),
        dbc.Checklist(
            options=['Show legend'],
            value=[],
            id="legend",
            switch=True,
            style={'margin-top': '10px'}
        ),
    ], style={'overflow-y': 'scroll', 'max-height': 'calc(100vh - 154px)'}),
    dbc.CardFooter([
        html.Div(['Data from ', html.A('phillipreeve.net', href="https://phillipreeve.net/blog/fe-list/", target='_blank')]),
        html.Div(['Feature requests, bugs: ', html.A('github', href='https://github.com/asgerlh/sony_fe_lens_chart', target='_blank')]),
    ], style={'text-align': 'center', 'font-size': '80%'}),
])

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(controls, sm=6, md=5, lg=4, xl=3, xxl=2, align='center', style={'padding': '12px'}),
        dbc.Col(dcc.Graph(id='graph', config={'displayModeBar': False}, style={'height': '100vh'}), style={'padding': '0'})
    ])
], fluid=True)


@app.callback(
    Output('graph', 'figure'),
    Input('manufacturer', 'value'),
    Input('prime-vs-zoom', 'value'),
    Input('focus', 'value'),
    Input('exif', 'value'),
    Input('focal-slider', 'value'),
    Input('aperture-slider', 'value'),
    Input('weight-slider', 'value'),
    Input('magnification-slider', 'value'),
    Input('price-slider', 'value'),
    Input('filter', 'value'),
    Input('legend', 'value')
    )
def update_figure(
        sel_manufacturer,
        sel_prime_vs_zoom,
        sel_focus,
        sel_exif,
        sel_focal_length,
        sel_aperture,
        sel_weight,
        sel_magnification,
        sel_price,
        sel_filter,
        sel_legend):
    focal_length = (df['Focal Length'].apply(lambda fl : fl.max()) >= 2**sel_focal_length[0]) & (df['Focal Length'].apply(lambda fl : fl.min()) <= 2**sel_focal_length[1])
    aperture = (df['Aperture'].apply(lambda fl : fl.max()) >= 2**sel_aperture[0]) & (df['Aperture'].apply(lambda fl : fl.min()) <= 2**sel_aperture[1])
    weight = (df.Weight >= 2**sel_weight[0]) & (df.Weight <= 2**sel_weight[1])
    magnification = (df.Magnification >= 2**sel_magnification[0]) & (df.Magnification <= 2**sel_magnification[1])
    price = (df.Price >= 2**sel_price[0]) & (df.Price <= 2**sel_price[1])

    if not sel_prime_vs_zoom:
        prime_vs_zoom = True
    elif 'Zoom' in sel_prime_vs_zoom:
        prime_vs_zoom = df['Focal Length'].apply(lambda fl : len(fl) > 1)
    else: # 'Prime'
        prime_vs_zoom = df['Focal Length'].apply(lambda fl : len(fl) == 1)

    if not sel_manufacturer:
        manufacturer = True
    else:
        manufacturer = df.Manufacturer.isin(sel_manufacturer)

    if sel_focus in ['AF', 'MF']:
        focus = df.Focus == sel_focus
    else:
        focus = True

    if sel_exif in ['Yes', 'No']:
        exif = df.Exif == sel_exif
    else:
        exif = True

    if not sel_filter:
        filter_dia = True
    else:
        filter_dia = df['Filter Diameter'].isin(sel_filter)

    filtered_df = df[manufacturer & prime_vs_zoom & focus & exif & focal_length & aperture & weight & magnification & price & filter_dia]

    fig = px.line(
        data_frame=filtered_df.explode(['Focal Length', 'Aperture']),
        x='Focal Length',
        y='Aperture',
        color='Lens',
        log_x=True,
        log_y=True,
    )
    fig.update_traces(
        mode="lines+markers",
    )

    for idx, t in enumerate(fig.data):
        d = filtered_df.iloc[idx]
        size = 25*(d['Weight']/500)**(0.7)
        opacity = 0.4*500/(d['Weight']+500) + 0.1
        t.opacity = opacity
        t.marker.size = size
        t.line.width = size
        t.line.color = colors[d['Manufacturer']]
        t.hovertemplate = \
            f"{d['Lens']}<br>"\
            f"{d['Focus']}"\
            f"{', No Exif' if d['Exif'] == False else ''}, "\
            f"1:{np.round(1/d['Magnification'],1)} ({d['Close Focusing Distance']}cm), "\
            f"ø{d['Filter Diameter']}<br>"\
            f"{d['Weight']}g, "\
            f"ø{d['Diameter']}mm x {d['Length']}mm"\
            "<extra></extra>"

    fig.update_layout(
        showlegend=True if 'Show legend' in sel_legend else False,
        title_x=0.5,
        margin=dict(t=30, r=20, l=64, b=60, pad=0),
        xaxis=dict(tickmode='array', tickvals=[10, 12, 16, 20, 24, 28, 35, 50, 70, 85, 100, 135, 150, 200, 250, 300, 400, 500, 600]),
        yaxis=dict(tickmode='array', tickvals=[1, 1.4, 2, 2.8, 4, 5.6, 8, 11, 16], automargin=True),
        transition_duration=500
    )

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
