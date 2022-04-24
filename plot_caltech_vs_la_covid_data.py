"""
Plot Caltech Covid-19 data and compare with LA County data.

Caltech dataset first transcribed from 
https://together.caltech.edu/cases-testing-and-tracing/case-log 
on 2021-08-04. Omitted cases where people lived out of state 
and/or had not accessed campus since March 2020. 
Date indicates the date that a case was posted on the case log 
(not the date the people tested positive). Dataset is updated 
manually.

LA County data sourced from the New York Times Github at
https://github.com/nytimes/covid-19-data/.
"""

import datetime
import numpy as np
import pandas as pd
import itertools

import bokeh.resources
import bokeh.plotting
import bokeh.io
import bokeh.embed

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

# Set line plot colors
cit_avg_color = '#f2cc44'
la_color = '#a369d6'

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

def plot_weekly_whole_pandemic(df_weekly_sum, df_total_rolling, df_la):
    """
    Plot the whole pandemic. 
    Stacked bars by affiliation for weekly Caltech cases. 
    7-day rolling averages for Caltech and LA County.
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
    max_avg_cases = df_total_rolling['case'].max()
    max_la_cases = df_la['cases_avg'].max()

    p = bokeh.plotting.figure(
        frame_width=800,
        frame_height=300,
        x_axis_label='date',
    #     y_axis_label='cases',
        x_axis_type='datetime',
        toolbar_location='above',
        tools=['hover', 'wheel_zoom', 'reset', 'pan', 'box_zoom'],
        tooltips="week of @date_tooltip: @$name $name",
    )

    # Set multiple y-ranges and add to plot
    p.y_range = bokeh.models.Range1d(start=-max_weekly_cases/40, end=max_weekly_cases*1.15)
    p.extra_y_ranges = {
        'cit_avg_y_range': bokeh.models.Range1d(start=-max_avg_cases/40, end=max_avg_cases*1.15),
        'la_y_range': bokeh.models.Range1d(start=-max_la_cases/40, end=max_la_cases*1.15)
    }

    p.add_layout(
        bokeh.models.LinearAxis(
            y_range_name='cit_avg_y_range', 
            axis_line_color=cit_avg_color, 
            major_tick_line_color=cit_avg_color,
            major_label_text_color=cit_avg_color,
            minor_tick_line_color=cit_avg_color,
             axis_label='cases', 
    #         axis_label_text_color=cit_avg_color,
        ), 
        'left',
    )

    p.add_layout(
        bokeh.models.LinearAxis(
            y_range_name='la_y_range', 
            axis_line_color=la_color,
            major_tick_line_color=la_color,
            major_label_text_color=la_color,
            minor_tick_line_color=la_color,
    #         axis_label='LA County daily average',
    #         axis_label_text_color=la_color,
        ), 
        'right',
    )

    # Set legend outside (hacky)
    p.add_layout(bokeh.models.Legend(), 'right')

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

    # Add line for LA County 7-day rolling average
    p.line(
        source=df_la,
        x='date', 
        y='cases_avg', 
        y_range_name='la_y_range',
        color=la_color, 
        line_width=2,
        legend_label='LA County daily average',
    )

    # Add line for Caltech 7-day rolling average
    p.line(
        x=df_total_rolling['date'], 
        y=df_total_rolling['case'], 
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

def plot_daily_90_day_view(df, df_total_rolling, df_la):
    """
    Plot the 90 day view. 
    Stacked bars by affiliation for daily Caltech cases. 
    7-day rolling averages for Caltech and LA County.
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
    max_avg_cases = df_total_rolling['case'].max()
    max_la_cases = df_la['cases_avg'].max()

    p = bokeh.plotting.figure(
        frame_width=800,
        frame_height=300,
        x_axis_label='date',
        y_axis_label='cases',
        x_axis_type='datetime',
        toolbar_location='above',
        tools=['pan', 'hover', 'wheel_zoom', 'reset', 'xwheel_pan', 'box_zoom'],
        active_scroll='xwheel_pan',
        tooltips="@date_tooltip: @$name $name",
    )

    # Set multiple y-ranges and add to plot
    p.y_range = bokeh.models.Range1d(start=-max_cases/40, end=max_cases*1.15)
    p.extra_y_ranges = {
        'la_y_range': bokeh.models.Range1d(start=-max_la_cases/40, end=max_la_cases*1.15)
    }

    p.add_layout(
        bokeh.models.LinearAxis(
            y_range_name='la_y_range', 
            axis_line_color=la_color,
            major_tick_line_color=la_color,
            major_label_text_color=la_color,
            minor_tick_line_color=la_color,
    #         axis_label='LA County daily average',
    #         axis_label_text_color=la_color,
        ), 
        'right',
    )

    p.add_layout(bokeh.models.Legend(), 'right')

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

    # Add line for LA County 7-day rolling average
    p.line(
        source=df_la,
        x='date', 
        y='cases_avg', 
        y_range_name='la_y_range',
        color=la_color, 
        line_width=2,
        legend_label='LA County daily average',
    )

    # Add line for Caltech 7-day rolling average
    p.line(
        x=df_total_rolling['date'], 
        y=df_total_rolling['case'],
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

if __name__ == '__main__':
    
    # Load Caltech data
    df, all_dates, affiliations = load_caltech_data()
    df_weekly_sum = caltech_weekly_sums(df)
    df_total_rolling = caltech_daily_average(df)
    
    # Load LA data
    df_la = load_la_data()
    
    # Generate plots
    p1 = plot_weekly_whole_pandemic(df_weekly_sum, df_total_rolling, df_la)
    p1_filename = 'covid_cases_la_caltech_weekly_whole_pandemic'
    
    p2 = plot_daily_90_day_view(df, df_total_rolling, df_la)
    p2_filename = 'covid_cases_la_caltech_daily_90_days'
    
    plots = [p1, p2]
    filenames = [p1_filename, p2_filename]
    
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
    
    
    # Save html objects
    bokeh.io.save(
        p1, 
        filename=f'{p1_filename}.html', 
        title='Caltech Weekly Covid Cases'
    )
    bokeh.io.save(
        p2, 
        filename=f'{p2_filename}.html', 
        title='Caltech Daily Covid Cases'
    )
    
    # Save pngs
    bokeh.io.export_png(
        p1, 
        filename=f'{p1_filename}.png', 
    )
    bokeh.io.export_png(
        p2, 
        filename=f'{p2_filename}.png', 
    )