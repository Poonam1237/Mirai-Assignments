import os
import pandas as pd
import streamlit as st
from google import genai

st.set_page_config(
    page_title="Life-OS",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0b1020;
}
.block-container {
    max-width: 1400px;
    padding-top: 2rem;
}
[data-testid="stMetric"] {
    background: #151c31;
    border: 1px solid #2b3655;
    border-radius: 14px;
    padding: 18px;
}
[data-testid="stSidebar"] {
    background: #101629;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Life-OS")
st.subheader("Digital Wellbeing Command Center")
st.caption("Track your screen time. Understand your habits. Reclaim your time.")

try:
    df = pd.read_csv("screentime.csv")
except FileNotFoundError:
    st.error("screentime.csv was not found. Please add it to the project folder.")
    st.stop()

required_columns = [
    "Date",
    "App_Name",
    "Category",
    "Minutes_Used"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"Missing columns in screentime.csv: {', '.join(missing_columns)}"
    )
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Minutes_Used"] = pd.to_numeric(
    df["Minutes_Used"],
    errors="coerce"
).fillna(0)

df = df.dropna(subset=["Date"])

dates = sorted(df["Date"].dt.date.unique())

st.sidebar.title("⚙️ Life-OS Controls")

selected_date = st.sidebar.selectbox(
    "📅 Select Day",
    dates,
    index=len(dates) - 1
)

daily_goal = st.sidebar.slider(
    "🎯 Daily Screen-Time Goal",
    min_value=60,
    max_value=720,
    value=240,
    step=15
)

st.sidebar.divider()

st.sidebar.markdown("### 📌 About")
st.sidebar.write(
    "Life-OS analyzes your digital behavior and uses Gemini "
    "to provide personalized lifestyle recommendations."
)

today_data = df[df["Date"].dt.date == selected_date]

total_minutes = int(today_data["Minutes_Used"].sum())

if not today_data.empty:
    app_usage = (
        today_data.groupby("App_Name")["Minutes_Used"]
        .sum()
        .sort_values(ascending=False)
    )

    most_used_app = app_usage.index[0]
    most_used_app_minutes = int(app_usage.iloc[0])
else:
    most_used_app = "None"
    most_used_app_minutes = 0

goal_difference = total_minutes - daily_goal

if goal_difference > 0:
    goal_delta = f"{goal_difference} min over goal"
else:
    goal_delta = f"{abs(goal_difference)} min under goal"

st.markdown(
    f"""
    <div style="
        background: linear-gradient(135deg, #151c31, #202b49);
        padding: 28px;
        border-radius: 18px;
        margin-bottom: 25px;
        border: 1px solid #303d61;
    ">
        <h1 style="margin-bottom:5px;">📡 Daily Command Center</h1>
        <p style="color:#aab5d1; margin:0;">
            Monitoring digital behavior for {selected_date}
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "📱 Screen Time",
        f"{total_minutes} min",
        f"{total_minutes / 60:.1f} hrs"
    )

with col2:
    st.metric(
        "🔥 Most Used App",
        most_used_app,
        f"{most_used_app_minutes} min"
    )

with col3:
    st.metric(
        "🎯 Daily Goal",
        f"{daily_goal} min",
        goal_delta,
        delta_color="inverse"
    )

with col4:
    goal_percentage = (
        (total_minutes / daily_goal) * 100
        if daily_goal > 0
        else 0
    )

    st.metric(
        "📊 Goal Usage",
        f"{goal_percentage:.0f}%"
    )

st.divider()

st.subheader("📈 14-Day Screen-Time Trend")

daily_usage = (
    df.groupby("Date")["Minutes_Used"]
    .sum()
    .sort_index()
)

st.line_chart(daily_usage)

st.subheader("📊 Category Breakdown")

category_usage = (
    today_data.groupby("Category")["Minutes_Used"]
    .sum()
    .sort_values(ascending=False)
)

col1, col2 = st.columns([2, 1])

with col1:
    if not category_usage.empty:
        st.bar_chart(category_usage)

with col2:
    st.markdown("### Today's Usage")

    if total_minutes > 0:
        for category, minutes in category_usage.items():
            percentage = (minutes / total_minutes) * 100

            st.write(f"**{category}**")
            st.progress(min(int(percentage), 100))
            st.caption(
                f"{int(minutes)} minutes • {percentage:.1f}%"
            )

st.divider()

st.subheader("📱 App Usage")

if not today_data.empty:
    st.bar_chart(app_usage)

st.divider()

st.subheader("🤖 Gemini Life Coach")

if total_minutes > daily_goal * 1.5:
    severity = "CRITICAL"
    st.error("🚨 Critical digital overload detected.")
elif total_minutes > daily_goal:
    severity = "HIGH"
    st.warning("⚠️ Screen time is above your daily goal.")
elif total_minutes > daily_goal * 0.75:
    severity = "MODERATE"
    st.info("ℹ️ Screen time is approaching your daily limit.")
else:
    severity = "LOW"
    st.success("✅ Excellent digital discipline today.")

def create_data_bridge(data):
    category_summary = (
        data.groupby("Category")["Minutes_Used"]
        .sum()
        .sort_values(ascending=False)
    )

    app_summary = (
        data.groupby("App_Name")["Minutes_Used"]
        .sum()
        .sort_values(ascending=False)
    )

    category_string = category_summary.to_string()
    app_string = app_summary.to_string()

    return category_string, app_string

category_string, app_string = create_data_bridge(today_data)

prompt = f"""
You are Life-OS, a brutal-but-fair holistic productivity and lifestyle coach.

Analyze this user's screen-time data.

DATE:
{selected_date}

TOTAL SCREEN TIME:
{total_minutes} minutes

DAILY GOAL:
{daily_goal} minutes

GOAL DIFFERENCE:
{goal_difference} minutes

SEVERITY:
{severity}

CATEGORY USAGE:
{category_string}

APP USAGE:
{app_string}

Analyze the user's actual behavior.

Do not simply say "use your phone less."

Identify the biggest source of excessive screen usage.

Distinguish productive screen time from recreational screen time.

Explain what the usage pattern suggests about the user's behavior.

Recommend specific physical and real-world replacements.

For excessive social media usage, suggest alternatives such as walking,
exercise, reading, meeting friends, hobbies, or outdoor activities.

For excessive entertainment usage, suggest concrete offline activities.

If coding or education usage is high, recognize that this may be productive.

Give a realistic action plan for tomorrow.

Be direct, honest, practical, and constructive.

Do not insult the user.

Use Markdown headings and bullet points.

Keep the response between 300 and 500 words.

End with exactly one concrete challenge under:

## 🎯 24-Hour Challenge
"""

api_key = (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
)

if api_key:

    if st.button(
        "🧠 Analyze My Digital Habits",
        use_container_width=True
    ):

        try:
            client = genai.Client(api_key=api_key)

            with st.spinner(
                "Gemini is analyzing your digital behavior..."
            ):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

            st.markdown("### 🧠 Life-OS Analysis")
            st.markdown(response.text)

        except Exception as error:
            st.error(f"Gemini API error: {error}")

else:
    st.warning(
        "Gemini is disabled. Add GEMINI_API_KEY to Streamlit secrets."
    )

st.divider()

st.subheader("🔗 Accountability Link")

st.write(
    "Share your selected day's screen-time statistics "
    "with an accountability partner."
)

share_url = (
    f"?date={selected_date}"
    f"&minutes={total_minutes}"
)

st.code(share_url, language="text")

st.info(
    f"📅 {selected_date}  |  "
    f"📱 {total_minutes} minutes"
)

st.caption(
    "Append these parameters to your deployed URL "
    "to share your daily statistics."
)

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        padding:20px;
        color:#8793ad;
    ">
        <h3>⚡ Life-OS</h3>
        <p>Data → Insights → Action</p>
        <p>Build better habits. Reclaim your time.</p>
    </div>
    """,
    unsafe_allow_html=True
)
