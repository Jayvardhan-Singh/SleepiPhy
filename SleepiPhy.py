import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import pytz # Added to handle timezone correctly on cloud servers

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SleepiPhy", page_icon="🌙", layout="wide", initial_sidebar_state="expanded")

# --- HELPER FUNCTIONS ---
def time_to_datetime(target_time, base_time, base_date):
    """Converts a time object to a datetime object, handling the midnight rollover."""
    dt = datetime.combine(base_date, target_time)
    if base_time.hour >= 12 and target_time.hour < 12:
        dt += timedelta(days=1)
    elif base_time.hour < 12 and target_time.hour >= 12:
        dt -= timedelta(days=1)
    return dt

def format_timedelta(td):
    """Formats a timedelta object into a clean 'Xh Ym' string."""
    total_seconds = int(td.total_seconds())
    if total_seconds < 0:
        return "Invalid (Negative)"
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours}h {minutes}m"

def get_time_str(dt):
    """Helper to format datetime into a clean 12-hour string."""
    return dt.strftime("%I:%M %p").lstrip("0")

# --- UI LOGIC ---
st.title("🌙 Comprehensive Sleep & Fasting Report")
st.markdown("Fill out your details. Hover over the chart and click the **camera icon** to download your complete report.")

# Sidebar: User Details
st.sidebar.header("User Details")
user_name = st.sidebar.text_input("Name", value="Sleepyhead")
user_age = st.sidebar.number_input("Age", min_value=1, max_value=120, value=30)

# Sidebar: Chronological Night Log
st.sidebar.header("Log Your Timeline")
last_meal = st.sidebar.time_input("1. Last meal before bed", value=datetime.strptime("19:30", "%H:%M").time())
screen_time = st.sidebar.time_input("2. Last screen time", value=datetime.strptime("22:45", "%H:%M").time())
bed_start = st.sidebar.time_input("3. Got into bed", value=datetime.strptime("22:00", "%H:%M").time())
sleep_start = st.sidebar.time_input("4. Decided to sleep (Lights out)", value=datetime.strptime("23:00", "%H:%M").time())
sleep_end = st.sidebar.time_input("5. Woke up", value=datetime.strptime("06:30", "%H:%M").time())
bed_end = st.sidebar.time_input("6. Got out of bed", value=datetime.strptime("07:00", "%H:%M").time())
first_meal = st.sidebar.time_input("7. First meal after waking", value=datetime.strptime("08:30", "%H:%M").time())

# --- DATA PROCESSING ---
base_date = date.today()

# Get local time for the timestamp (Servers default to UTC, this grabs local user time if possible or you can set a specific timezone)
# Example defaults to system time, but you can explicitly set local tz like pytz.timezone('Asia/Kolkata') if needed.
current_time_str = datetime.now().strftime("%I:%M %p")

# Convert all times to datetimes relative to bed_start
dt_bed_start = datetime.combine(base_date, bed_start)
dt_bed_end = time_to_datetime(bed_end, bed_start, base_date)
dt_sleep_start = time_to_datetime(sleep_start, bed_start, base_date)
dt_sleep_end = time_to_datetime(sleep_end, bed_start, base_date)
dt_last_meal = time_to_datetime(last_meal, bed_start, base_date)
dt_screen_time = time_to_datetime(screen_time, bed_start, base_date)
dt_first_meal = time_to_datetime(first_meal, bed_start, base_date)

# Calculate Intervals
time_in_bed = dt_bed_end - dt_bed_start
approx_sleep = dt_sleep_end - dt_sleep_start
meal_to_sleep = dt_sleep_start - dt_last_meal
screen_to_sleep = dt_sleep_start - dt_screen_time
fasting_interval = dt_first_meal - dt_last_meal
efficiency = (approx_sleep.total_seconds() / time_in_bed.total_seconds()) * 100 if time_in_bed.total_seconds() > 0 else 0

# --- VISUALIZATION ---
fig = go.Figure()

# Base Layer: Time in Bed
fig.add_trace(go.Scatter(
    x=[dt_bed_start, dt_bed_end], y=["Timeline", "Timeline"],
    mode="lines", line=dict(color="#B0C4DE", width=60), name="Time in Bed", hoverinfo="name"
))

# Top Layer: Approximate Time Slept
fig.add_trace(go.Scatter(
    x=[dt_sleep_start, dt_sleep_end], y=["Timeline", "Timeline"],
    mode="lines", line=dict(color="#4169E1", width=30), name="Approx. Sleep", hoverinfo="name"
))

# Annotations (Time Labels)
fig.add_annotation(x=dt_bed_start, y="Timeline", text=f"In Bed<br><b>{get_time_str(dt_bed_start)}</b>", showarrow=False, yshift=-45, font=dict(size=11, color="#607B96"))
fig.add_annotation(x=dt_bed_end, y="Timeline", text=f"Out of Bed<br><b>{get_time_str(dt_bed_end)}</b>", showarrow=False, yshift=-45, font=dict(size=11, color="#607B96"))
fig.add_annotation(x=dt_sleep_start, y="Timeline", text=f"Decided to Sleep<br><b>{get_time_str(dt_sleep_start)}</b>", showarrow=False, yshift=45, font=dict(size=11, color="#27408B"))
fig.add_annotation(x=dt_sleep_end, y="Timeline", text=f"Woke Up<br><b>{get_time_str(dt_sleep_end)}</b>", showarrow=False, yshift=45, font=dict(size=11, color="#27408B"))

# Vertical Lines
fig.add_vline(x=dt_last_meal.timestamp() * 1000, line_dash="dot", line_color="orange", annotation_text=f"Last Meal<br><b>{get_time_str(dt_last_meal)}</b>", annotation_position="top left", annotation_font_color="orange")
fig.add_vline(x=dt_screen_time.timestamp() * 1000, line_dash="dash", line_color="red", annotation_text=f"Last Screen<br><b>{get_time_str(dt_screen_time)}</b>", annotation_position="bottom right", annotation_font_color="red")
fig.add_vline(x=dt_first_meal.timestamp() * 1000, line_dash="dot", line_color="green", annotation_text=f"First Meal<br><b>{get_time_str(dt_first_meal)}</b>", annotation_position="top right", annotation_font_color="green")

# --- EMBEDDING METRICS INTO THE CHART ---
metrics_html = (
    f"<b>Time in Bed:</b> {format_timedelta(time_in_bed)} &nbsp;&nbsp;|&nbsp;&nbsp; "
    f"<b>Approx. Sleep:</b> {format_timedelta(approx_sleep)} &nbsp;&nbsp;|&nbsp;&nbsp; "
    f"<b>Est. Efficiency:</b> {efficiency:.1f}%<br>"
    f"<b>Last Meal to Lights Out:</b> {format_timedelta(meal_to_sleep)} &nbsp;&nbsp;|&nbsp;&nbsp; "
    f"<b>Screen to Lights Out:</b> {format_timedelta(screen_to_sleep)} &nbsp;&nbsp;|&nbsp;&nbsp; "
    f"<b>Fasting Window:</b> {format_timedelta(fasting_interval)}"
)

fig.add_annotation(
    xref="paper", yref="paper", x=0.5, y=-0.4,
    showarrow=False, text=metrics_html, font=dict(size=13, color="#333"),
    align="center", bgcolor="#F4F6F9", bordercolor="#D1D5DB", borderwidth=1, borderpad=10
)

# Layout Formatting
report_date = base_date.strftime('%B %d, %Y')
fig.update_layout(
    title=dict(
        text=f"<b>Nightly Sleep & Fasting Report</b><br><span style='font-size:14px; color:gray;'>User: {user_name} (Age: {user_age}) | Generated: {report_date} at {current_time_str}</span>",
        x=0.5,
        xanchor='center'
    ),
    # THE FIX IS HERE: type='date' forces a chronological scale regardless of the environment
    xaxis=dict(type='date', showticklabels=False, gridcolor='rgba(0,0,0,0)', zeroline=False),
    yaxis=dict(showticklabels=False, zeroline=False),
    plot_bgcolor="white",
    paper_bgcolor="white", 
    height=550, 
    margin=dict(t=120, b=150, l=40, r=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5)
)

# Render Plotly Chart
st.plotly_chart(fig, use_container_width=True)
