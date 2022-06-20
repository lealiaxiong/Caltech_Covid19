"""
Plot Caltech Covid-19 data and compare with LA County data.

Caltech dataset `caltech_covid_cases.csv` first transcribed from 
https://together.caltech.edu/cases-testing-and-tracing/case-log 
on 2021-08-04. Excluded cases where people lived out of state 
and/or had not accessed campus in one month 
(included in `caltech_covid_cases_excluded.csv`. 
Date indicates the date that a case was posted on the case log 
(not the date of a positive test). Dataset is updated 
manually.

LA County data sourced from the New York Times Github at
https://github.com/nytimes/covid-19-data/.
"""

import datetime
import numpy as np
import pandas as pd
import itertools

import sklearn.linear_model
import sklearn.preprocessing
import sklearn.mixture
import scipy.spatial

import bokeh.resources
import bokeh.plotting
import bokeh.io
import bokeh.embed

import colorcet
import holoviews as hv
from holoviews.plotting.links import DataLink
hv.extension('bokeh')

# WHO declares pandemic
start_date = datetime.date(2020, 3, 11)
# Start on a Sunday
start_date -= datetime.timedelta(days=start_date.weekday()) + datetime.timedelta(days=1)

# How people are affiliated with Caltech (subject to change)
affiliations_ordered = [          
    'employees',
    'campus employees', 
    'off-campus employees',
    'CCC employees',
    'external affiliates',
    'postdocs', 
    'faculty',
    'students', 
    'undergraduate students',
    'graduate students',    
]
color_ordered = [    
    '#87aac0',
    '#4384b1',
    '#326386',
    '#1c374a',
    '#9e9e9e',
    '#b38c00',
    '#8a5500',    
    '#e75a0d',
    '#f47e3e',
    '#ca6702',  
]

# Set plot colors
cit_avg_color = '#f2cc44'
cit_area_color = '#f47e3e'
la_area_color = '#a168c4'
category_cmap = colorcet.b_glasbey_hv[:2] + colorcet.b_glasbey_hv[3:4] + colorcet.b_glasbey_hv[9:]

# Load and organize data

def load_caltech_data(start_date=start_date, data_source='caltech_covid_cases.csv'):
    """
    Loads Caltech data.
    Returns DataFrame of Caltech cases, NumPy array of dates,
    NumPy array of Caltech affiliations."""
    df = pd.read_csv(data_source).astype({'date': 'datetime64[D]'})
    
    # Date of last update
    current_date = df.iloc[-1]['date'].date()
    
    all_dates = np.arange(
        start_date, 
        current_date + datetime.timedelta(days=1), 
        dtype='datetime64[D]'
    )
    
    # Fill in dates with no cases
    affiliations = df['affiliation'].unique()
    for affiliation in affiliations:
        df_blank = pd.DataFrame(columns=['date', 'case', 'affiliation'])
        df_blank['date'] = all_dates
        df_blank['case'] = 0
        df_blank['affiliation'] = affiliation
        df = pd.concat([df, df_blank]).sort_values('date')
        
    # One row per date
    df = df.groupby(['date', 'affiliation']).sum().reset_index()
        
    return df, all_dates, affiliations

def caltech_weekly_sums(df):
    """
    Compute total weekly cases by affiliation.
    Returns DataFrame of total weekly cases by affiliation. 
    """
    # Sum by week
    df_copy = df.copy()
    df_copy['date'] = df_copy['date'] - pd.to_timedelta(7, unit='d')

    df_weekly_sum = df_copy.groupby(
        [
            'affiliation', 
            pd.Grouper(key='date', freq='W')
        ]
    )[
        'case'
    ].sum(
    ).reset_index(
    ).sort_values(
        'date'
    ).rename(
        columns={'date': 'week of', 'case': 'total cases'}
    ).reset_index(
    )

    # Remove week of 2020-03-01 ('-1th week')
    df_weekly_sum.drop(
        list(
            np.arange(
                len(
                    df_weekly_sum['affiliation'].unique()
                )
            )
        ), 
        axis=0, 
        inplace=True
    )
    
    return df_weekly_sum

def caltech_daily_average(df):
    """
    Sum all new cases per day and compute 7-day rolling average
    Returns DataFrame of daily average new cases.
    """
    # Total cases regardless of affiliation
    df_total = df.groupby('date').sum().sort_values('date')
    
    # Compute 7-day rolling average
    df_total_rolling = df_total.rolling(7).mean().reset_index()
    
    return df_total_rolling

def load_la_data():
    """
    Load LA County data from .csv outputted from import_la_county_data.py
    Returns DataFrame of LA County data.
    """
    
    df_la = pd.read_csv('los_angeles_covid_cases.csv').astype({'date': 'datetime64[D]'})
    df_la['date_tooltip'] = df_la['date'].astype('str')
    
    return df_la

def combine_data(df_total_rolling, df_la):
    """
    Merge Caltech daily average and LA County daily average data.
    """
    return df_la.merge(df_total_rolling)

# Process data

def clustering_by_ratio(df_all):
    """
    Cluster dates by ratio of Caltech daily average to LA County daily average 
    using Gaussian mixture model with Dirichlet process prior.
    
    Returns DataFrame with cluster labels.
    """
    df_all['caltech / la'] = df_all['caltech_cases_avg'] / df_all['cases_avg']
    
    # Preprocess data
    X = df_all['caltech / la'].to_numpy().reshape(-1, 1)
    transformer = sklearn.preprocessing.RobustScaler().fit(X)
    X_scaled = transformer.transform(X)
    
    # Clustering
    gmm = sklearn.mixture.BayesianGaussianMixture(
        n_components=12, 
        covariance_type='full',
        random_state=0
    ).fit(X_scaled)
    
    labels = gmm.predict(X_scaled)
    
    label_map = {label: i + 1 for i, label in enumerate(np.unique(labels))}
    
    df_all['label'] = labels
    df_all['label'] = df_all['label'].map(lambda x: label_map[x])
    
    return df_all

def lin_reg_by_cluster(df_all):
    """
    Perform linear regression on each cluster.
    
    Returns DataFrame with new column for predicted values.
    """
    if 'label' not in df_all.columns:
        df_all = clustering_by_ratio(df_all)
        
    for label in np.unique(df_all['label']):    
        X = np.array(df_all.loc[df_all['label'] == label]['cases_avg']).reshape(-1, 1)
        y = np.array(df_all.loc[df_all['label'] == label]['caltech_cases_avg']).reshape(-1, 1)

        reg = sklearn.linear_model.LinearRegression(fit_intercept=False).fit(X, y)

        y_reg = reg.predict(X)

        df_all.loc[df_all['label'] == label, 'y_reg'] = y_reg
        
    return df_all

# Plotting
def plot_weekly_whole_pandemic(df_weekly_sum, df_all):
    """
    Plot the whole pandemic. 
    Stacked bars by affiliation for weekly Caltech cases. 
    7-day rolling averages for Caltech.
    """
    
    # Set up data for stacked bars
    data = {
        affiliation: np.array(
            df_weekly_sum.loc[df_weekly_sum['affiliation'] == affiliation]['total cases']
        ) for affiliation in affiliations_ordered
    }
    data['date'] = np.array(
        (df_weekly_sum['week of'] + pd.DateOffset(days=3.5)).unique()
    )
    data['date_tooltip'] = np.array((df_weekly_sum['week of'].astype('str').unique()))

    # Set up maximum cases for setting y-axis bound
    max_weekly_cases = df_weekly_sum.groupby('week of').sum()['total cases'].max()
    max_avg_cases = df_all['caltech_cases_avg'].max()

    p = bokeh.plotting.figure(
        sizing_mode='stretch_width',
        frame_height=300,
        max_width=1150,
        min_width=600,
        x_axis_label='date',
        y_axis_label='weekly cases',
        x_axis_type='datetime',
        toolbar_location='above',
        tools=['hover', 'xpan', 'wheel_zoom', 'reset', 'pan', 'box_zoom'],
        tooltips="week of @date_tooltip: @$name $name",
    )
    
    p.toolbar.active_drag = None

    # Set multiple y-ranges and add to plot
    p.y_range = bokeh.models.Range1d(start=-max_weekly_cases/40, end=max_weekly_cases*1.15)
    p.extra_y_ranges = {
        'cit_avg_y_range': bokeh.models.Range1d(start=-max_avg_cases/40, end=max_avg_cases*1.15),
    }

    p.add_layout(
        bokeh.models.LinearAxis(
            y_range_name='cit_avg_y_range', 
            axis_line_color=cit_avg_color, 
            major_tick_line_color=cit_avg_color,
            major_label_text_color=cit_avg_color,
            minor_tick_line_color=cit_avg_color,
            axis_label='daily average', 
            axis_label_text_color=cit_avg_color,
        ), 
        'right',
    )


    # Set legend outside (hacky)
    p.add_layout(bokeh.models.Legend(), 'left')

    # Add stacked bars for Caltech weekly total cases
    bars = p.vbar_stack(
        affiliations_ordered,
        source=data,
        x='date',
        legend_label=affiliations_ordered,
        color=color_ordered,
        line_color='black',
        width=datetime.timedelta(days=7),
    )

    # Add line for Caltech 7-day rolling average
    p.line(
        x=df_all['date'], 
        y=df_all['caltech_cases_avg'], 
        y_range_name='cit_avg_y_range',
        color=cit_avg_color, 
        line_width=2,
        legend_label='Caltech daily average',
    )

    # Only show tooltips on stacked bars
    p.hover.renderers = bars

    # Label when Caltech data last updated since I do it by hand
    last_updated_str = np.array(df_total_rolling['date'].dt.strftime('%Y-%m-%d'))[-1]
    p.add_layout(
        bokeh.models.Title(
            text=f"Caltech data last updated: {last_updated_str}", 
            align="right", 
            text_color="grey"
        ), 
        "below"
    )


    # Plot styling
    p.legend.title = 'weekly cases'
    p.legend.location = 'top_left'
    p.legend.border_line_color = None
    p.legend.background_fill_alpha = 0
    p.legend.orientation = 'vertical'

    p.xgrid.visible = False
    p.outline_line_alpha = 0

    p.xaxis.major_label_orientation = np.pi/4
    p.x_range.start = df_weekly_sum['week of'].iloc[0]
    p.x_range.end = df_weekly_sum['week of'].iloc[-1] + pd.DateOffset(days=7)

    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.major_label_text_font_size = '12pt'

    p.xaxis.ticker = (
        pd.to_datetime(df_weekly_sum['week of'].unique()).view(int) / 10**6
    )[::4]
    p.xaxis.ticker.minor_ticks = (
        pd.to_datetime(df_weekly_sum['week of'].unique()).view(int) / 10**6)
    
    p.xaxis.formatter = bokeh.models.DatetimeTickFormatter(days=["%Y-%m-%d"])

    return p

def plot_daily_90_day_view(df, df_all):
    """
    Plot the 90 day view. 
    Stacked bars by affiliation for daily Caltech cases. 
    7-day rolling averages for Caltech.
    Pan in time by scrolling.
    """
    
    current_date = df.iloc[-1]['date'].date()
    last_90_days = np.arange(
        current_date - datetime.timedelta(days=89), 
        current_date + datetime.timedelta(days=1), 
        dtype='datetime64[D]'
    )
    
    df_90 = df.loc[df['date'].isin(last_90_days)]
    
    # Set up data for stacked bars
    data = {
        affiliation:np.array(df.loc[df['affiliation'] == affiliation]['case'])
        for affiliation in affiliations_ordered
    }
    data['date'] = np.array(df['date'].unique())
    data['date_tooltip'] = np.array((df['date'].astype('str').unique()))

    # Set up maximum cases for setting y-axis bound
    max_cases = df.groupby('date').sum()['case'].max()
    max_avg_cases = df_all['caltech_cases_avg'].max()

    p = bokeh.plotting.figure(
        sizing_mode='stretch_width',
        frame_height=300,
        max_width=1150,
        min_width=600,
        x_axis_label='date',
        y_axis_label='cases',
        x_axis_type='datetime',
        toolbar_location='above',
        tools=['pan', 'hover', 'wheel_zoom', 'reset', 'xpan', 'box_zoom'],
        active_drag='xpan',
        tooltips="@date_tooltip: @$name $name",
    )

    # Set multiple y-ranges and add to plot
    p.y_range = bokeh.models.Range1d(start=-max_cases/40, end=max_cases*1.15)

    p.add_layout(bokeh.models.Legend(), 'left')

    # Add stacked bars for new cases each day
    bars = p.vbar_stack(
        affiliations_ordered,
        source=data,
        x='date',
        legend_label=affiliations_ordered,
        color=color_ordered,
        line_color='black',
        width=datetime.timedelta(days=1),
    )

    # Add line for Caltech 7-day rolling average
    p.line(
        x=df_all['date'], 
        y=df_all['caltech_cases_avg'],
        color=cit_avg_color, 
        line_width=2,
        legend_label='Caltech daily average',
    )

    # Only show tooltips on stacked bars
    p.hover.renderers = bars

    # Label when Caltech data last updated since I do it by hand
    p.add_layout(
        bokeh.models.Title(text=f"Caltech data last updated: {str(current_date)}", 
                           align="right", text_color="grey"), "below"
    )

    # Plot styling
    # p.legend.location = 'top_right'
    p.legend.border_line_color = None
    p.legend.background_fill_alpha = 0
    p.legend.orientation = 'vertical'

    p.xgrid.visible = False
    p.outline_line_alpha = 0

    p.xaxis.major_label_orientation = np.pi/4
    p.x_range.start = df_90['date'].iloc[0] - pd.DateOffset(days=0.5)
    p.x_range.end = df_90['date'].iloc[-1] + pd.DateOffset(days=0.5)

    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.major_label_text_font_size = '12pt'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.major_label_text_font_size = '12pt'

    p.xaxis.ticker = (pd.to_datetime(data['date']).view(int) / 10**6)[::7]
    p.xaxis.ticker.minor_ticks = (pd.to_datetime(data['date']).view(int) / 10**6)
    p.xaxis.formatter = bokeh.models.DatetimeTickFormatter(days=["%Y-%m-%d"])

    return p

def plot_clustering_results_correlation(df_all, df_weekly_sum):
    """
    Plot clustering results with scatter of Caltech vs LA County 
    daily average and Caltech daily average over time 
    with linked brushing using box select or lasso select tools.
    """
    # Hulls for Caltech vs. LA County scatter
    hulls = []
    hull_polys = []

    for label, color in zip(np.unique(df_all['label']), category_cmap):    
        points = df_all.loc[df_all['label'] == label][['cases_avg', 'caltech_cases_avg']].to_numpy()
        hull = scipy.spatial.ConvexHull(points)
        hulls.append(hull)
        hull_poly = hv.Polygons(
            zip([points[vertex][0] for vertex in hull.vertices], [points[vertex][1] for vertex in hull.vertices])
        ).opts(color=color, alpha=0.2, line_alpha=0)
        hull_polys.append(hull_poly)
    
    hull_polys_plot = hv.Overlay(hull_polys)
    
    # Lin regs for each cluster on Caltech vs. LA County scatter
    lin_regs_plot = hv.Curve(
        data=df_all,
        kdims=['cases_avg'],
        vdims=['y_reg', 'label']
    ).groupby(
        'label'
    ).opts(
        color=hv.Cycle(category_cmap),
        line_dash='dashed'
    ).overlay(
    ).opts(
        legend_position='top_left'
    )
    
    # Caltech vs. LA County scatter
    correlation_scatter = hv.Scatter(
        data=df_all,
        kdims=['cases_avg'],
        vdims=['caltech_cases_avg', 'label'],
    ).opts(
        xlabel='LA County daily average',
        ylabel='Caltech daily average',
        frame_width=400,
        frame_height=400,
        tools=['hover'],
        size=8,
        color='label',
    )

    # Correlation plot 
    correlation_plot = hull_polys_plot * correlation_scatter * lin_regs_plot
    
    
    # Area curves for Caltech and LA daily average over time
    caltech_area = hv.Area(
        data=df_all,
        kdims=['date'],
        vdims=['caltech_cases_avg'],
        label='Caltech daily average',
    ).opts(
        color=cit_area_color,
        alpha=0.5,
        frame_width=800,
        frame_height=300,
        line_color=cit_area_color,
    )
    
    df_all['la cases_avg / 1000'] = df_all['cases_avg'] / 1000

    la_area = hv.Area(
        data=df_all,
        kdims=['date'],
        vdims=['la cases_avg / 1000'],
        label='LA County daily average / 1000',
    ).opts(
        color=la_area_color,
        alpha=0.2,
        frame_width=800,
        frame_height=300,
        line_color=la_area_color,
    )
    
    # Caltech daily average over time
    caltech_scatter = hv.Scatter(
        data=df_all,
        kdims=['date'],
        vdims=['caltech_cases_avg', 'label']
    ).opts(
        size=8,
        tools=['hover'],
        frame_width=800,
        frame_height=300,
        padding=0.05,
        color='label',
        legend_position='top_left'
    )

    caltech_plot = (la_area * caltech_area * caltech_scatter).opts(ylabel='daily average')
    
    # Link scatter plots
    dlink = DataLink(correlation_scatter, caltech_scatter)
    
    caltech_vs_la = (
        correlation_plot.opts(
            frame_width=300, frame_height=300
        ) 
        + caltech_plot.opts(
            frame_width=600, frame_height=300
        )
    ).opts(
        hv.opts.Scatter(
            tools=['box_select', 'lasso_select'],
            cmap=category_cmap[:len(np.unique(df_all['label']))],
        )
    )
    
    # Render to Bokeh and style
    layout = hv.render(caltech_vs_la)
    
    for p in layout.children[1].children[0][0], layout.children[1].children[1][0]:
        p.xgrid.visible = False
        p.outline_line_alpha = 0
        p.xaxis.axis_label_text_font_size = '14pt'
        p.xaxis.major_label_text_font_size = '12pt'
        p.yaxis.axis_label_text_font_size = '14pt'
        p.yaxis.major_label_text_font_size = '12pt'
        p.toolbar.active_drag = bokeh.models.LassoSelectTool()
        
    # Modify datetime ticker
    p = layout.children[1].children[1][0]
    p.xaxis.ticker = (
        pd.to_datetime(df_weekly_sum['week of'].unique()).view(int) / 10**6
    )[::4]
    p.xaxis.ticker.minor_ticks = (
        pd.to_datetime(df_weekly_sum['week of'].unique()).view(int) / 10**6)

    p.xaxis.formatter = bokeh.models.DatetimeTickFormatter(days=["%Y-%m-%d"])

    p.xaxis.major_label_orientation = np.pi/4
    
    return layout

if __name__ == '__main__':
    
    # Load Caltech data
    df, all_dates, affiliations = load_caltech_data()
    df_weekly_sum = caltech_weekly_sums(df)
    df_total_rolling = caltech_daily_average(df).dropna().rename(columns={'case': 'caltech_cases_avg'})
    
    # Load LA data
    df_la = load_la_data()
    
    # Combine rolling average data
    df_all = combine_data(df_total_rolling, df_la)
    
    # Clustering
    df_all = lin_reg_by_cluster(df_all)
    
    # Generate plots
    p1 = plot_weekly_whole_pandemic(df_weekly_sum, df_all)
    p1_filename = 'covid_cases_la_caltech_weekly_whole_pandemic'
    
    p2 = plot_daily_90_day_view(df, df_all)
    p2_filename = 'covid_cases_la_caltech_daily_90_days'
    
    p3 = plot_clustering_results_correlation(df_all, df_weekly_sum)
    p3_filename = 'covid_cases_cluster_by_ratio'
    
    plots = [p1, p2, p3]
    filenames = [p1_filename, p2_filename, p3_filename]
    titles = [
        'Caltech weekly covid cases', 
        'Caltech daily covid cases',
        'Cluster by Caltech / LA ratio',
    ]
    
    # Save embedding objects
    js_files = [f'{filename}.js' for filename in filenames]
    tag_files = [f'{filename}_tag.html' for filename in filenames]
    
    for i, plot in enumerate(plots):
        js_file = js_files[i]
        tag_file = tag_files[i]
        
        js, tag = bokeh.embed.autoload_static(plot, bokeh.resources.CDN, js_file)
        
        with open(js_file, 'w') as text_file:
            text_file.write(js)
        with open(tag_file, 'w') as text_file:
            text_file.write(tag)
    
    
    # Save html objects and pngs
    for p, filename, title in zip(plots, filenames, titles):
        bokeh.io.save(
            p, 
            filename=f'{filename}.html', 
            title=title
        )
        bokeh.io.export_png(
            p, 
            filename=f'{filename}.png', 
        )