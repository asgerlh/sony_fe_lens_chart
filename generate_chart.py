import pandas as pd
import numpy as np
import plotly.express as px

file = 'Sony FE lens list by phillipreeve.net cleaned.xlsx'
df1 = pd.read_excel(file, sheet_name='All')
df2 = pd.read_excel(file, sheet_name='no exif')

df1['Exif'] = True
df2['Exif'] = False

df = pd.concat((df1, df2))

df = df.rename(columns={
    'Focal\nLength': 'Focal Length',
    'Front Filter \nDiameter': 'Filter Diameter',
    'Close\nFocusing\nDistance ': 'Close Focusing Distance',
    'optical \nstabilizer': 'Optical Stabilizer',
    'Aperture\nBlades': 'Aperture Blades',
    'Elements/\nGroups': 'Elements & Groups',
    'List Price \n(please check \nfor actual)': 'List Price',
    'Used price\n (average \nauction 7/20)': 'Used price',
    'Comment, \nResources': 'Comments',
    'Price \n(please check \nfor current)': 'Price'
})

def str2list(d):
    if isinstance(d, str):
        d = [float(f) for f in d.split(',')]
    return d

def focal_length_and_speed_as_list(d):
    f = np.atleast_1d(str2list(d['Focal Length']))
    s = np.atleast_1d(str2list(d['Speed']))

    if s.shape[-1] < f.shape[-1]:
        s = np.repeat(s, f.shape[-1])

    d['Focal Length'] = f
    d['Speed'] = s
    return d

df = df.apply(focal_length_and_speed_as_list, axis=1)

df = df.sort_values(by='Weight', ascending=False)

colors = {m: c for m, c in zip(df['Manufacturer'].unique(), px.colors.qualitative.Light24)}

fig = px.line(
    data_frame=df.explode(['Focal Length', 'Speed']),
    x='Focal Length',
    y='Speed',
    color='Lens',
    template='plotly_dark',
    log_x=True,
    log_y=True,
    title='<b>Sony FE Lens Chart</b><br>List by <a href="https://phillipreeve.net/blog/fe-list/">phillipreeve.net</a><br>Size indicates weight',
)
fig.update_traces(
    mode="lines+markers",
)

for idx, t in enumerate(fig.data):
    d = df.iloc[idx]
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
    title_x=0.5,
    xaxis=dict(tickmode='array', tickvals=[10, 12, 16, 20, 24, 28, 35, 50, 70, 85, 100, 135, 150, 200, 250, 300, 400, 500, 600]),
    yaxis=dict(tickmode='array', tickvals=[1, 1.4, 2, 2.8, 4, 5.6, 8, 11, 16]),
)

filename = 'docs/index.html'

html = fig.write_html(filename, include_plotlyjs='cdn')

with open(filename, 'r') as original: data = original.read()
with open(filename, 'w') as modified: modified.write("<style>body {margin:0;}</style>\n" + data)