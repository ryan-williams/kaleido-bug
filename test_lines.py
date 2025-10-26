
import pandas as pd
import plotly.express as px
from datetime import datetime

# The lines() function from the notebook
def lines(
    df, name, xname, y_fmt,
    hoverx=True, dir='img',
    legend_lr=False,
    ax_offset=None,
    ay_offsets=None,
    h_line=None,
    xtick=None, xtickformat=None,
    ytick=None, ytickformat=None,
    show=default_show,
    w=1000, h=600,
    **kwargs,
):
    fig = px.line(
        df.reset_index(),
        x='month',
        labels={
            'variable': '',
            'value': xname,
            'month': '',
        }
    )
    idx = df.index.to_series()
    for k, ay_offset in zip(df, ay_offsets):
        x = idx.iloc[-1]
        y = df[k].iloc[-1]
        x_str = x.strftime("%b '%y")
        y_str = format(y, y_fmt)
        # Note: Using simple annotations without ax/ay for kaleido compatibility
        fig.add_annotation(
            x=x,
            y=y + ay_offset,
            text=f'{x_str}: {y_str}',
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-40 if ay_offset > 0 else 40,
        )
    if h_line is not None:
        fig.add_hline(y=h_line, line=dict(color='#777', width=1)),
    fig = plots.save(
        fig,
        name=name,
        x=dict(dtick=xtick, tickformat=xtickformat),
        y=dict(dtick=ytick, tickformat=ytickformat),
        legend=(
            dict(
                yanchor="bottom",
                y=0.03,
                xanchor="right",
                x=0.99,
            ) if legend_lr else dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
            )
        ),
        hoverx=hoverx,
        dir=dir,
        w=w, h=h,
        **kwargs,
    )
    return export(fig, name, show=show)

# Test it
mt = pd.DataFrame({
    'avg weekday': [252769, 261472, 269794],
    'avg weekend': [95527, 100742, 113074],
}, index=pd.date_range('2012-01', periods=3, freq='MS'))
mt.index.name = 'month'

df = mt[['avg weekday', 'avg weekend']].rename(columns={
    'avg weekday': 'Avg Weekday',
    'avg weekend': 'Avg Weekend',
})

print("DataFrame structure:")
print(df)
print()
print("Index name:", df.index.name)
print("Index dtype:", df.index.dtype)
print()

# Now try reset_index
df_reset = df.reset_index()
print("After reset_index():")
print(df_reset)
print("Columns:", df_reset.columns.tolist())
print("Column dtypes:")
print(df_reset.dtypes)
