import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="SleepPhy", page_icon="🌙", layout="wide")

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
    """Helper to format datetime into a clean 12-hour string (e.g., '10:30 PM')."""
    return dt.strftime("%I:%M %p").lstrip("0") # lstrip removes leading zeros (e.g., '08' -> '8')

# --- UI LOGIC ---
st.title("🌙 Sleep Hygiene Visualizer")
st.markdown("Enter your metrics below to generate a layered timeline of your night and calculate your hygiene gaps.")

st.sidebar.header("Log Your Night")

# 1. Time in Bed Inputs
st.sidebar.subheader("Time in Bed")
bed_start = st.sidebar.time_input("Got into bed at", value=datetime.strptime("22:00", "%H:%M").time())
bed_end = st.sidebar.time_input("Got out of bed at", value=datetime.strptime("07:00", "%H:%M").time())

# 2. Actual Sleep Inputs
st.sidebar.subheader("Actual Sleep")
sleep_start = st.sidebar.time_input("Fell asleep at", value=datetime.strptime("23:00", "%H:%M").time())
sleep_end = st.sidebar.time_input("Woke up at", value=datetime.strptime("06:30", "%H:%M").time())

# 3 & 4. Event Inputs
st.sidebar.subheader("Meals & Hygiene")
last_meal = st.sidebar.time_input("Last meal before bed", value=datetime.strptime("19:30", "%H:%M").time())
screen_time = st.sidebar.time_input("Last screen time", value=datetime.strptime("22:45", "%H:%M").time())
first_meal = st.sidebar.time_input("First meal after waking", value=datetime.strptime("08:30", "%H:%M").time())

# --- DATA PROCESSING ---
base_date = date.today()

# Convert all times to datetimes
dt_bed_start = datetime.combine(base_date, bed_start)
dt_bed_end = time_to_datetime(bed_end, bed_start, base_date)

dt_sleep_start = time_to_datetime(sleep_start, bed_start, base_date)
dt_sleep_end = time_to_datetime(sleep_end, bed_start, base_date)

dt_last_meal = time_to_datetime(last_meal, bed_start, base_date)
dt_screen_time = time_to_datetime(screen_time, bed_start, base_date)
dt_first_meal = time_to_datetime(first_meal, bed_start, base_date)

# Calculate Intervals
time_in_bed = dt_bed_end - dt_bed_start
actual_sleep = dt_sleep_end - dt_sleep_start
meal_to_sleep = dt_sleep_start - dt_last_meal
screen_to_sleep = dt_sleep_start - dt_screen_time
fasting_interval = dt_first_meal - dt_last_meal

# --- VISUALIZATION ---
fig = go.Figure()

# Base Layer: Time in Bed
fig.add_trace(go.Scatter(
    x=[dt_bed_start, dt_bed_end],
    y=["Sleep Timeline", "Sleep Timeline"],
    mode="lines",
    line=dict(color="#B0C4DE", width=60), # Light Steel Blue, slightly thicker
    name="Time in Bed",
    hoverinfo="name"
))

# Top Layer: Actual Time Slept
fig.add_trace(go.Scatter(
    x=[dt_sleep_start, dt_sleep_end],
    y=["Sleep Timeline", "Sleep Timeline"],
    mode="lines",
    line=dict(color="#4169E1", width=30), # Royal Blue
    name="Actual Sleep",
    hoverinfo="name"
))

# --- CREATIVE TIME ANNOTATIONS ---

# 1. Annotate Bed Times (Floating below the bars)
fig.add_annotation(x=dt_bed_start, y="Sleep Timeline", text=f"In Bed<br><b>{get_time_str(dt_bed_start)}</b>", 
                   showarrow=False, yshift=-45, font=dict(size=11, color="#607B96"), align="center")
fig.add_annotation(x=dt_bed_end, y="Sleep Timeline", text=f"Out of Bed<br><b>{get_time_str(dt_bed_end)}</b>", 
                   showarrow=False, yshift=-45, font=dict(size=11, color="#607B96"), align="center")

# 2. Annotate Sleep Times (Floating above the bars)
fig.add_annotation(x=dt_sleep_start, y="Sleep Timeline", text=f"Fell Asleep<br><b>{get_time_str(dt_sleep_start)}</b>", 
                   showarrow=False, yshift=45, font=dict(size=11, color="#27408B"), align="center")
fig.add_annotation(x=dt_sleep_end, y="Sleep Timeline", text=f"Woke Up<br><b>{get_time_str(dt_sleep_end)}</b>", 
                   showarrow=False, yshift=45, font=dict(size=11, color="#27408B"), align="center")

# 3. Vertical Line: Last Meal (Time embedded in label)
fig.add_vline(
    x=dt_last_meal.timestamp() * 1000, 
    line_dash="dot", line_color="orange", 
    annotation_text=f"Last Meal<br><b>{get_time_str(dt_last_meal)}</b>", 
    annotation_position="top left", annotation_font_color="orange"
)

# 4. Vertical Line: Last Screen Time (Time embedded in label)
fig.add_vline(
    x=dt_screen_time.timestamp() * 1000, 
    line_dash="dash", line_color="red", 
    annotation_text=f"Last Screen<br><b>{get_time_str(dt_screen_time)}</b>", 
    annotation_position="bottom right", annotation_font_color="red"
)

# 5. Vertical Line: First Meal (Time embedded in label)
fig.add_vline(
    x=dt_first_meal.timestamp() * 1000, 
    line_dash="dot", line_color="green", 
    annotation_text=f"First Meal<br><b>{get_time_str(dt_first_meal)}</b>", 
    annotation_position="top right", annotation_font_color="green"
)

# Layout Formatting
fig.update_layout(
    title="Nightly Sleep Pattern & Hygiene Analysis",
    xaxis_title="", # Removed title to clean up space
    yaxis_title="",
    height=400,
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # Moved legend to top
    xaxis=dict(
        showticklabels=False, # We hid the confusing 2-hour ticks completely!
        gridcolor='rgba(0,0,0,0.05)', # Ultra faint grid
        zeroline=False
    ),
    yaxis=dict(showticklabels=False, zeroline=False), # Hide the "Sleep Timeline" y-axis text
    plot_bgcolor="white",
    margin=dict(t=80, b=40) # Adjust margins to fit annotations
)

# Render Plotly Chart
st.plotly_chart(fig, use_container_width=True)

# --- METRICS DASHBOARD ---
st.markdown("### 📊 Your Nightly Insights")
st.markdown("---")

# Row 1: Core Sleep & Fasting
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Time in Bed", format_timedelta(time_in_bed))
with col2:
    st.metric("Actual Time Slept", format_timedelta(actual_sleep))
with col3:
    st.metric("Total Fasting Window", format_timedelta(fasting_interval))

st.markdown("<br>", unsafe_allow_html=True) 

# Row 2: Sleep Hygiene Gaps
col4, col5, col6 = st.columns(3)
with col4:
    st.metric("Last Meal to Sleep", format_timedelta(meal_to_sleep))
with col5:
    st.metric("Screen Time to Sleep", format_timedelta(screen_to_sleep))
with col6:
    efficiency = (actual_sleep.total_seconds() / time_in_bed.total_seconds()) * 100 if time_in_bed.total_seconds() > 0 else 0
    st.metric("Sleep Efficiency", f"{efficiency:.1f}%")
