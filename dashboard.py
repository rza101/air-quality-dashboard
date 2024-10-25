import calendar
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# functions
def convert_pm25_to_aqi(pm25):
    if pm25 >= 225.5:
        return 'Hazardous'
    elif pm25 >= 125.5:
        return 'Very Unhealthy'
    elif pm25 >= 55.5:
        return 'Unhealthy'
    elif pm25 >= 35.5:
        return 'Unhealthy for Sensitive Groups'
    elif pm25 >= 9.1:
        return 'Moderate'
    else:
        return 'Good'


# data loading
df_aq_full = pd.read_csv('PRSA_Data_20130301-20170228.csv', parse_dates=['dt'])
aq_stations = df_aq_full['station'].unique()

# variables
AQ_PARAMETER_COLUMNS = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

# UI code
st.set_page_config(
    page_title='Air Quality Dashboard',
    layout='wide'
)

st.header('Air Quality Dashboard')

hourly_tab, hourly_avg_tab, daily_avg_tab, monthly_avg_tab, yearly_avg_tab, per_station_avg_tab = st.tabs(
    ['Hourly', 'Hourly Average', 'Daily Average', 'Monthly Average',
        'Yearly Average', 'Per station Average']
)

with hourly_tab:
    st.subheader('Hourly Air Quality')

    hourly_date_start_col1, hourly_date_start_col2 = st.columns(2)

    with hourly_date_start_col1:
        hourly_date_start = st.date_input(
            key='hourly_date_start',
            label='Start Date',
            min_value=df_aq_full['dt'].min(),
            max_value=df_aq_full['dt'].max(),
            value=df_aq_full['dt'].max(),
        )

    with hourly_date_start_col2:
        hourly_time_start = st.time_input(
            key='hourly_time_start',
            label='Start Time',
            step=dt.timedelta(hours=1),
            value=df_aq_full['dt'].min(),
        )

    hourly_date_end_col1, hourly_date_end_col2 = st.columns(2)

    with hourly_date_end_col1:
        hourly_date_end = st.date_input(
            key='hourly_date_end',
            label='End Date',
            min_value=df_aq_full['dt'].min(),
            max_value=df_aq_full['dt'].max(),
            value=df_aq_full['dt'].max(),
        )

    with hourly_date_end_col2:
        hourly_time_end = st.time_input(
            key='hourly_time_end',
            label='End Time',
            step=dt.timedelta(hours=1),
            value=df_aq_full['dt'].max(),
        )

    hourly_dt_start = dt.datetime.combine(
        hourly_date_start, hourly_time_start)
    hourly_dt_end = dt.datetime.combine(
        hourly_date_end, hourly_time_end)

    hourly_stations = st.multiselect(
        key='hourly_stations',
        label='Select the station(s), leave empty to select from all stations',
        options=aq_stations,
    )

    if len(hourly_stations) == 0:
        hourly_stations = list(aq_stations)

    hourly_dt_start = dt.datetime.combine(hourly_date_start, hourly_time_start)
    hourly_dt_end = dt.datetime.combine(hourly_date_end, hourly_time_end)

    df_aq_hourly = df_aq_full.query(
        'dt >= @hourly_dt_start & dt <= @hourly_dt_end & station in @hourly_stations'
    )

    fig, axes = plt.subplots(3, 2)
    fig.set_figwidth(15)
    fig.set_figheight(15)
    fig.suptitle(f'Hourly Pollutant Concentration ({
                 hourly_dt_start} - {hourly_dt_end})')

    for index, column in enumerate(AQ_PARAMETER_COLUMNS):
        ax = axes[index//2, index % 2]

        if column == 'PM2.5':
            ax.axhspan(0, 9, color='#abd162', alpha=0.5, label='Good')
            ax.axhspan(9, 35.5, color='#f8d461', alpha=0.5, label='Moderate')
            ax.axhspan(35.5, 55.4, color='#fb9956', alpha=0.5,
                       label='Unhealthy for Sensitive Groups')
            ax.axhspan(55.4, 125.5, color='#f6686a',
                       alpha=0.5, label='Unhealthy')
            ax.axhspan(125.5, 225.5, color='#a47db8',
                       alpha=0.5, label='Very Unhealthy')
            ax.axhspan(225.5, 225.5 if df_aq_hourly[column].max(
            ) <= 225.5 else df_aq_hourly[column].max()*1.2, color='#a07785', alpha=0.5, label='Hazardous')

        for station, df_station in df_aq_hourly.groupby('station'):
            df_station = df_station.set_index('dt').sort_index()
            ax.plot(df_station[column], 'o-', label=station)

        ax.set_title(column)
        ax.set_ylim(bottom=0, top=df_aq_hourly[column].max()*1.2)

    legend_labels = [
        'Good',
        'Moderate',
        'Unhealthy for Sensitive Groups',
        'Unhealthy',
        'Very Unhealthy',
        'Hazardous',
    ]
    legend_labels.extend(hourly_stations)

    fig.legend(
        loc='center right',
        bbox_to_anchor=(1.2, 0.5),
        labels=legend_labels
    )
    fig.text(0, -0.025, f'Stations: {', '.join(hourly_stations)}')
    fig.tight_layout()

    st.pyplot(fig)

with hourly_avg_tab:
    st.subheader('Hourly Average Air Quality')

    hourly_avg_date = st.date_input(
        key='hourly_avg_date',
        label='Select the date or date range (average will be calculated from the range)',
        format='YYYY/MM/DD',
        min_value=df_aq_full['dt'].min(),
        max_value=df_aq_full['dt'].max(),
        value=[df_aq_full['dt'].max(), df_aq_full['dt'].max()]
    )
    hourly_avg_stations = st.multiselect(
        key='hourly_avg_stations',
        label='Select the station(s), leave empty to select from all stations',
        options=aq_stations,
    )

    hourly_avg_date_start = hourly_avg_date[0]
    hourly_avg_date_end = hourly_avg_date[1] if len(
        hourly_avg_date) == 2 else hourly_avg_date[0]

    if len(hourly_avg_stations) == 0:
        hourly_avg_stations = list(aq_stations)

    hourly_avg_dt_start = dt.datetime.combine(
        hourly_avg_date[0], dt.time(0, 0, 0))
    hourly_avg_dt_end = dt.datetime.combine(
        hourly_avg_date_end, dt.time(23, 59, 59))

    df_aq_hourly_avg = df_aq_full.query(
        'dt >= @hourly_avg_dt_start & dt <= @hourly_avg_dt_end & station in @hourly_avg_stations'
    ).groupby('hour')[AQ_PARAMETER_COLUMNS].mean(numeric_only=True)

    fig, axes = plt.subplots(2, 3)
    fig.set_figwidth(15)
    fig.set_figheight(7.5)
    fig.suptitle(f'Hourly Average Pollutant Concentration ({
        hourly_avg_dt_start} - {hourly_avg_dt_end})')

    for index, column in enumerate(AQ_PARAMETER_COLUMNS):
        ax = axes[index//3, index % 3]

        if column == 'PM2.5':
            ax.axhspan(0, 9, color='#abd162', alpha=0.5, label='Good')
            ax.axhspan(9, 35.5, color='#f8d461', alpha=0.5, label='Moderate')
            ax.axhspan(35.5, 55.4, color='#fb9956', alpha=0.5,
                       label='Unhealthy for Sensitive Groups')
            ax.axhspan(55.4, 125.5, color='#f6686a',
                       alpha=0.5, label='Unhealthy')
            ax.axhspan(125.5, 225.5, color='#a47db8',
                       alpha=0.5, label='Very Unhealthy')
            ax.axhspan(225.5, 225.5 if df_aq_hourly_avg[column].max(
            ) <= 225.5 else df_aq_hourly_avg[column].max()*1.2, color='#a07785', alpha=0.5, label='Hazardous')

        ax.plot(df_aq_hourly_avg[column], 'o-')
        ax.set_title(column)
        ax.set_xticks(range(0, 24, 3))
        ax.set_xticklabels([dt.time(hour).strftime('%H:%M')
                            for hour in range(0, 24, 3)])
        ax.set_ylim(bottom=0, top=df_aq_hourly_avg[column].max()*1.2)

    fig.legend(loc='center right', bbox_to_anchor=(1.2, 0.5))
    fig.text(0, -0.025, f'Stations: {', '.join(hourly_avg_stations)}')
    fig.tight_layout()

    st.pyplot(fig)

with daily_avg_tab:
    st.subheader('Daily Average Air Quality')

    daily_avg_date = st.date_input(
        key='daily_avg_date',
        label='Select the date range, range that is less than 7 days are calculated as a week from start date',
        format='YYYY/MM/DD',
        min_value=df_aq_full['dt'].min(),
        max_value=df_aq_full['dt'].max(),
        value=[df_aq_full['dt'].max() - pd.Timedelta(6, 'd'),
               df_aq_full['dt'].max()]
    )
    daily_avg_stations = st.multiselect(
        key='daily_avg_stations',
        label='Select the station(s), leave empty to select from all stations',
        options=aq_stations,
    )

    daily_avg_date_start = daily_avg_date[0]
    daily_avg_date_end = daily_avg_date[1] if len(
        daily_avg_date) == 2 else daily_avg_date[0]

    if daily_avg_date_end - daily_avg_date_start < dt.timedelta(days=6):
        daily_avg_date_end = daily_avg_date_start + dt.timedelta(days=6)

    if len(daily_avg_stations) == 0:
        daily_avg_stations = list(aq_stations)

    daily_avg_dt_start = dt.datetime.combine(
        daily_avg_date_start, dt.time(0, 0, 0))
    daily_avg_dt_end = dt.datetime.combine(
        daily_avg_date_end, dt.time(23, 59, 59))

    df_aq_daily_avg = df_aq_full.query(
        'dt >= @daily_avg_dt_start & dt <= @daily_avg_dt_end & station in @daily_avg_stations'
    ).groupby(df_aq_full['dt'].dt.day_of_week)[AQ_PARAMETER_COLUMNS].mean(numeric_only=True)

    fig, axes = plt.subplots(2, 3)
    fig.set_figwidth(15)
    fig.set_figheight(7.5)
    fig.suptitle(f'Daily Average Pollutant Concentration ({
                 daily_avg_dt_start} - {daily_avg_dt_end})')

    for index, column in enumerate(AQ_PARAMETER_COLUMNS):
        ax = axes[index//3, index % 3]

        if column == 'PM2.5':
            ax.axhspan(0, 9, color='#abd162', alpha=0.5, label='Good')
            ax.axhspan(9, 35.5, color='#f8d461', alpha=0.5, label='Moderate')
            ax.axhspan(35.5, 55.4, color='#fb9956', alpha=0.5,
                       label='Unhealthy for Sensitive Groups')
            ax.axhspan(55.4, 125.5, color='#f6686a',
                       alpha=0.5, label='Unhealthy')
            ax.axhspan(125.5, 225.5, color='#a47db8',
                       alpha=0.5, label='Very Unhealthy')
            ax.axhspan(225.5, 225.5 if df_aq_daily_avg[column].max(
            ) <= 225.5 else df_aq_daily_avg[column].max()*1.2, color='#a07785', alpha=0.5, label='Hazardous')

        ax.plot(df_aq_daily_avg[column], 'o-')
        ax.set_title(column)
        ax.set_xticks(df_aq_daily_avg.index)
        ax.set_xticklabels(calendar.day_abbr)
        ax.set_ylim(bottom=0, top=df_aq_daily_avg[column].max()*1.2)

    fig.legend(loc='center right', bbox_to_anchor=(1.2, 0.5))
    fig.text(0, -0.025, f'Stations: {', '.join(daily_avg_stations)}')
    fig.tight_layout()

    st.pyplot(fig)

with monthly_avg_tab:
    st.subheader('Monthly Average Air Quality')

    monthly_avg_years = st.multiselect(
        key='monthly_avg_years',
        label='Select the year(s), default to 2016',
        options=df_aq_full['year'].unique(),
        default=[2016]
    )
    monthly_avg_stations = st.multiselect(
        key='monthly_avg_stations',
        label='Select the station(s), leave empty to select from all stations',
        options=aq_stations,
    )

    if len(monthly_avg_years) == 0:
        monthly_avg_years = [2016]

    if len(monthly_avg_stations) == 0:
        monthly_avg_stations = list(aq_stations)

    monthly_avg_years.sort()

    df_aq_monthly_avg = df_aq_full.query(
        'year in @monthly_avg_years & station in @monthly_avg_stations'
    ).groupby('month')[AQ_PARAMETER_COLUMNS].mean(numeric_only=True)

    fig, axes = plt.subplots(2, 3)
    fig.set_figwidth(15)
    fig.set_figheight(7.5)
    fig.suptitle(f'Monthly Average Pollutant Concentration ({
                 ', '.join(map(str, monthly_avg_years))})')

    for index, column in enumerate(AQ_PARAMETER_COLUMNS):
        ax = axes[index//3, index % 3]

        if column == 'PM2.5':
            ax.axhspan(0, 9, color='#abd162', alpha=0.5, label='Good')
            ax.axhspan(9, 35.5, color='#f8d461', alpha=0.5, label='Moderate')
            ax.axhspan(35.5, 55.4, color='#fb9956', alpha=0.5,
                       label='Unhealthy for Sensitive Groups')
            ax.axhspan(55.4, 125.5, color='#f6686a',
                       alpha=0.5, label='Unhealthy')
            ax.axhspan(125.5, 225.5, color='#a47db8',
                       alpha=0.5, label='Very Unhealthy')
            ax.axhspan(225.5, 225.5 if df_aq_monthly_avg[column].max(
            ) <= 225.5 else df_aq_monthly_avg[column].max()*1.2, color='#a07785', alpha=0.5, label='Hazardous')

        ax.plot(df_aq_monthly_avg[column], 'o-')
        ax.set_title(column)
        ax.set_xticks(range(0, 13))
        ax.set_xticklabels(calendar.month_abbr)
        ax.set_ylim(bottom=0, top=df_aq_monthly_avg[column].max()*1.2)

    fig.legend(loc='center right', bbox_to_anchor=(1.2, 0.5))
    fig.text(0, -0.025, f'Stations: {', '.join(daily_avg_stations)}')
    fig.tight_layout()

    st.pyplot(fig)

with yearly_avg_tab:
    st.subheader('Yearly Average Air Quality Trend')

    df_aq_yearly_avg = df_aq_full.groupby(
        'year')[AQ_PARAMETER_COLUMNS].mean(numeric_only=True)

    fig, axes = plt.subplots(2, 3)
    fig.set_figwidth(15)
    fig.set_figheight(7.5)
    fig.suptitle('Yearly Average Pollutant Concentration')

    for index, column in enumerate(AQ_PARAMETER_COLUMNS):
        ax = axes[index//3, index % 3]

        if column == 'PM2.5':
            ax.axhspan(0, 9, color='#abd162', alpha=0.5, label='Good')
            ax.axhspan(9, 35.5, color='#f8d461', alpha=0.5, label='Moderate')
            ax.axhspan(35.5, 55.4, color='#fb9956', alpha=0.5,
                       label='Unhealthy for Sensitive Groups')
            ax.axhspan(55.4, 125.5, color='#f6686a',
                       alpha=0.5, label='Unhealthy')
            ax.axhspan(125.5, 225.5, color='#a47db8',
                       alpha=0.5, label='Very Unhealthy')
            ax.axhspan(225.5, 225.5 if df_aq_yearly_avg[column].max(
            ) <= 225.5 else df_aq_yearly_avg[column].max()*1.2, color='#a07785', alpha=0.5, label='Hazardous')

        ax.plot(df_aq_yearly_avg[column], 'o-')
        ax.set_title(column)
        ax.set_xticks(range(2013, 2018, 1))
        ax.set_ylim(bottom=0, top=df_aq_yearly_avg[column].max()*1.2)

    fig.legend(loc='center right', bbox_to_anchor=(1.2, 0.5))
    fig.text(0, -0.025, f'Stations: {', '.join(aq_stations)}')
    fig.tight_layout()

    st.pyplot(fig)

with per_station_avg_tab:
    st.subheader('Per-Station Average Air Quality')

    per_station_avg_date_start_col1, per_station_avg_date_start_col2 = st.columns(
        2)

    with per_station_avg_date_start_col1:
        per_station_avg_date_start = st.date_input(
            key='per_station_avg_date_start',
            label='Start Date',
            min_value=df_aq_full['dt'].min(),
            max_value=df_aq_full['dt'].max(),
            value=df_aq_full['dt'].min(),
        )

    with per_station_avg_date_start_col2:
        per_station_avg_time_start = st.time_input(
            key='per_station_avg_time_start',
            label='Start Time',
            step=dt.timedelta(hours=1),
            value=df_aq_full['dt'].min(),
        )

    per_station_avg_date_end_col1, per_station_avg_date_end_col2 = st.columns(
        2)

    with per_station_avg_date_end_col1:
        per_station_avg_date_end = st.date_input(
            key='per_station_avg_date_end',
            label='End Date',
            min_value=df_aq_full['dt'].min(),
            max_value=df_aq_full['dt'].max(),
            value=df_aq_full['dt'].max(),
        )

    with per_station_avg_date_end_col2:
        per_station_avg_time_end = st.time_input(
            key='per_station_avg_time_end',
            label='End Time',
            step=dt.timedelta(hours=1),
            value=df_aq_full['dt'].max(),
        )

    per_station_avg_dt_start = dt.datetime.combine(
        per_station_avg_date_start, per_station_avg_time_start)
    per_station_avg_dt_end = dt.datetime.combine(
        per_station_avg_date_end, per_station_avg_time_end)

    df_aq_per_station_avg = df_aq_full.query(
        'dt >= @per_station_avg_dt_start & dt <= @per_station_avg_dt_end'
    ).groupby('station')[AQ_PARAMETER_COLUMNS].mean(numeric_only=True)

    fig, axes = plt.subplots(2, 3)
    fig.set_figwidth(15)
    fig.set_figheight(7.5)
    fig.suptitle(f'Per-station Average Pollutant Concentration ({
                 per_station_avg_dt_start} - {per_station_avg_dt_end})')

    for index, column in enumerate(AQ_PARAMETER_COLUMNS):
        ax: plt.Axes = axes[index//3, index % 3]

        if column == 'PM2.5':
            ax.axvspan(0, 9, color='#abd162', label='Good')
            ax.axvspan(9, 35.5, color='#f8d461', label='Moderate')
            ax.axvspan(35.5, 55.4, color='#fb9956',
                       label='Unhealthy for Sensitive Groups')
            ax.axvspan(55.4, 125.5, color='#f6686a', label='Unhealthy')
            ax.axvspan(125.5, 225.5, color='#a47db8', label='Very Unhealthy')
            ax.axvspan(225.5, 225.5 if df_aq_per_station_avg[column].max(
            ) <= 225.5 else df_aq_per_station_avg[column].max()*1.2, label='Hazardous')

        ax.barh(df_aq_per_station_avg.index.sort_values(ascending=False),
                df_aq_per_station_avg[column].sort_index(ascending=False))
        ax.set_title(column)
        ax.set_xlim(left=0, right=df_aq_per_station_avg[column].max()*1.2)

    fig.legend(loc='center right', bbox_to_anchor=(1.2, 0.5))
    fig.tight_layout()

    st.pyplot(fig)
