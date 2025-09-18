import streamlit as st
from astral import LocationInfo
from astral.sun import sun
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import date
import pandas as pd
from geopy.geocoders import Nominatim
import plotly.graph_objects as go


def riseset(loc, date):
    timezone = ZoneInfo(loc.timezone)
    s = sun(loc.observer, date=date, tzinfo=timezone)
    sunrise = s["sunrise"].strftime("%H:%M")
    sunrise_f = s["sunrise"].hour + (s["sunrise"].minute / 60)
    sunset = s["sunset"].strftime("%H:%M")
    sunset_f = s["sunset"].hour + (s["sunset"].minute / 60)
    return sunrise, sunset, sunrise_f, sunset_f


# title
st.title('Sunrise & sunset time')
st.divider()

# define location
col1, col2, col3, col4 = st.columns(4)
with col2:
    city = st.text_input(label="City", value="Lentilly")
    geolocator = Nominatim(user_agent="geo_app")
    location = geolocator.geocode(city)

    tf = TimezoneFinder()
    tz = tf.timezone_at(lng=location.longitude, lat=location.latitude)

    city_request = LocationInfo(location.raw.get("display_name"),
                                location.raw.get("address", {}).get("country", ""),
                                tz,
                                location.latitude,
                                location.longitude)
with col3:
    st.write("city:", location.address)
    st.write("timezone", tz)
    st.write(f"coordinates: ({str(location.latitude)}, {str(location.longitude)})")

# display map
col1, col2, col3 = st.columns([1,3,1])
with col2:
    point = [{'latitude': location.latitude, 'longitude': location.longitude}]
    st.map(point, zoom=3, width=400, height=300, use_container_width=False)

# define date
today = date.today().isoformat()
current_year = date.today().year
col1, col2, col3 = st.columns([2,1,1])
with col1:
    year = st.multiselect(label="Year",
                        options=[i for i in range(current_year-2,current_year+3)],
                        default=[current_year],
                        max_selections=1,
                        )
with col2:
    input_date = st.text_input(label="Date", value=today)

# create date and time dataframe
dates = pd.date_range(start=f'1/1/{year[0]}', end=f'12/31/{year[0]}')
df = dates.to_frame(index=False, name="date")
df[["sunrise", "sunset", "sunrise_f", "sunset_f"]] = df.apply(lambda row: riseset(city_request, row['date']), axis=1, result_type='expand')

# display chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['date'], y=df['sunrise_f'],
                         mode='lines',
                         name='sunrise',
                         line=dict(color='green')
                        )
             )
fig.add_trace(go.Scatter(x=df['date'], y=df['sunset_f'],
                         mode='lines',
                         name='sunset',
                         line=dict(color='darkorange')
                        )
             )
fig.add_vline(x=date.today(),
              line_dash="dash",
              line_color="violet",
             )
fig.add_annotation(x=input_date,
                   y=2,
                   text=str(date.today()),
                   showarrow=False,
                   arrowhead=2,
                   arrowcolor="violet",
                   font=dict(size=14,
                             color="violet"),
                  )
fig.add_annotation(x=input_date,
                   y=df['sunrise_f'].loc[df['date']==input_date].iloc[0],
                   text=f"{df['sunrise'].loc[df['date']==input_date].iloc[0]}",
                   showarrow=True,
                   arrowhead=0,
                   arrowcolor="green",
                   font=dict(size=14,
                             color="green"),
                  )
fig.add_annotation(x=input_date,
                   y=df['sunset_f'].loc[df['date']==input_date].iloc[0],
                   text=f"{df['sunset'].loc[df['date']==input_date].iloc[0]}",
                   showarrow=True,
                   arrowhead=0,
                   arrowcolor="darkorange",
                   font=dict(size=14,
                             color="darkorange"),
                  )
first_days = df[df['date'].dt.day == 1]['date']
fig.update_xaxes(tickvals=first_days,
                 tickformat="    %b"
                )
fig.update_yaxes(range=[24,0],
                 tickvals=[6, 8, 12, 17, 21],
                 ticktext=[f"{h}:00" for h in [6, 8, 12, 17, 21]],
                )
fig.update_layout(title=dict(text=f"Sunrise and sunset times in {city} in {year[0]}",
                             #x=.5,
                            ),
                  width=700,
                  height=450,
                  margin=dict(l=50, r=50, t=50, b=50),
                  showlegend=False,
                  plot_bgcolor='cornsilk',
                 )

st.plotly_chart(fig)
