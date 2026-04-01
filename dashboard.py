"""
LeisureHub Analytics Dashboard
DAMG 6210 | Group 6
Rohith Sesham | Zenish Borad | Chandra Shekar | Sam Livingstone

Run:  streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from config import get_connection_string

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LeisureHub Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme ────────────────────────────────────────────────────────────────────
DARK        = True
FONT_COLOR  = "#e8eaf0" if DARK else "#0f1117"
MUTED_COLOR = "#8b95a8" if DARK else "#6b7280"
CARD_BG     = "#1e2130" if DARK else "#ffffff"
CARD_BORDER = "rgba(255,255,255,0.08)" if DARK else "rgba(0,0,0,0.08)"
PAGE_BG     = "#141720" if DARK else "#f5f7fa"
PLOT_BG     = "#1e2130" if DARK else "#ffffff"
GRID_COLOR  = "rgba(255,255,255,0.06)" if DARK else "rgba(0,0,0,0.06)"
AXIS_COLOR  = "rgba(255,255,255,0.15)" if DARK else "rgba(0,0,0,0.12)"
COLORS      = ["#4f7cff","#00c9a7","#ff6b6b","#ffa94d","#a29bfe","#74b9ff","#fd79a8","#55efc4"]

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=block');

html, body, [class*="st-"], [data-testid], p, div, span:not(.material-symbols-rounded), h1, h2, h3, h4, button, input, label {{
    font-family: 'Inter', sans-serif !important;
}}
.material-symbols-rounded {{
    font-family: 'Material Symbols Rounded' !important;
    font-size: 20px !important; font-style: normal !important;
    font-weight: normal !important; line-height: 1 !important;
    letter-spacing: normal !important; text-transform: none !important;
    white-space: nowrap !important; word-wrap: normal !important;
    direction: ltr !important; -webkit-font-smoothing: antialiased !important;
    font-feature-settings: 'liga' !important;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24 !important;
}}
[data-testid="stAppViewContainer"],
[data-testid="stAppViewBlockContainer"],
.main .block-container {{ background-color: {PAGE_BG} !important; }}
[data-testid="stSidebar"] {{
    background: #0d1017 !important;
    border-right: 1px solid rgba(255,255,255,0.06);
}}
[data-testid="stSidebar"] *:not(.material-symbols-rounded) {{ color: #c8cfe0 !important; }}
[data-testid="stSidebar"] .stRadio > label {{ display: none; }}
[data-testid="stIconMaterial"] {{
    font-family: 'Material Symbols Rounded', sans-serif !important;
    font-size: 20px !important; font-style: normal !important;
    line-height: 1 !important; letter-spacing: normal !important;
    text-transform: none !important; white-space: nowrap !important;
    -webkit-font-smoothing: antialiased !important;
    font-feature-settings: 'liga' 1 !important;
}}
[data-testid="collapsedControl"] [data-testid="stIconMaterial"],
[data-testid="baseButton-headerNoPadding"] [data-testid="stIconMaterial"] {{ font-size: 0 !important; }}
[data-testid="collapsedControl"] [data-testid="stIconMaterial"]::after {{
    content: '›'; font-size: 20px !important;
    font-family: 'Inter', sans-serif !important; color: #c8cfe0;
}}
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"]::after {{
    content: '‹'; font-size: 20px !important;
    font-family: 'Inter', sans-serif !important; color: #c8cfe0;
}}
.kpi-card {{
    background: {CARD_BG}; border: 1px solid {CARD_BORDER};
    border-radius: 14px; padding: 1.1rem 1.25rem;
    position: relative; overflow: hidden; margin-bottom: 1rem;
}}
.kpi-card::before {{
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #4f7cff, #00c9a7); border-radius: 14px 14px 0 0;
}}
.kpi-label {{ font-size: 11px; font-weight: 600; letter-spacing: 0.8px;
    text-transform: uppercase; color: {MUTED_COLOR}; margin-bottom: 8px; }}
.kpi-value {{ font-size: 26px; font-weight: 700; color: {FONT_COLOR}; line-height: 1; }}
.kpi-delta {{ font-size: 11px; color: #00c9a7; margin-top: 5px; font-weight: 500; }}
.chart-card {{
    background: {CARD_BG}; border: 1px solid {CARD_BORDER};
    border-radius: 14px; padding: 1.25rem 1.5rem 0.75rem; margin-bottom: 14px;
}}
.chart-title {{ font-size: 11px; font-weight: 600; letter-spacing: 0.8px;
    color: {MUTED_COLOR}; text-transform: uppercase; margin-bottom: 0.75rem; }}
.insight-box {{
    display: flex; align-items: flex-start; gap: 10px;
    background: rgba(79,124,255,0.10); border-left: 3px solid #4f7cff;
    border-radius: 0 10px 10px 0; padding: 0.7rem 1rem; margin-bottom: 8px;
    font-size: 13px; color: {FONT_COLOR};
}}
.insight-icon {{ font-size: 14px; margin-top: 1px; flex-shrink: 0; }}
.section-label {{
    font-size: 11px; font-weight: 600; letter-spacing: 1px;
    text-transform: uppercase; color: {MUTED_COLOR};
    margin: 1.25rem 0 0.75rem; padding-bottom: 6px;
    border-bottom: 1px solid {CARD_BORDER};
}}
.page-header {{ margin-bottom: 1.5rem; }}
.page-title  {{ font-size: 24px; font-weight: 700; color: {FONT_COLOR}; margin: 0; }}
.page-subtitle {{ font-size: 13px; color: {MUTED_COLOR}; margin-top: 3px; }}
.nav-section {{
    font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
    text-transform: uppercase; color: #4a5568 !important; padding: 0.5rem 0 0.25rem;
}}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
[data-testid="stDecoration"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)

# ── DB engine ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return create_engine(
        get_connection_string(),
        pool_size=3,
        max_overflow=2,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
    )

engine = get_engine()

# ── Data loaders ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_users():
    with engine.connect() as conn:
        conn.execute(text("OPEN SYMMETRIC KEY SYMKEY_LeisureHub DECRYPTION BY CERTIFICATE CERT_LeisureHub"))
        df = pd.read_sql("""
            SELECT user_id, name, age_group, available_hours_per_week, account_status,
                   CONVERT(VARCHAR(255), DECRYPTBYKEY(email_encrypted)) AS email,
                   ISNULL(TRY_CAST(
                       REPLACE(REPLACE(LTRIM(RTRIM(
                           CONVERT(VARCHAR(50), DECRYPTBYKEY(monthly_budget_encrypted))
                       )), CHAR(0), ''), CHAR(13), '')
                   AS DECIMAL(10,2)), 0.0) AS monthly_budget, created_at
            FROM USERS
        """, conn)
        conn.execute(text("CLOSE SYMMETRIC KEY SYMKEY_LeisureHub"))
    return df

@st.cache_data(ttl=300)
def load_engagement():
    with engine.connect() as conn:
        conn.execute(text("OPEN SYMMETRIC KEY SYMKEY_LeisureHub DECRYPTION BY CERTIFICATE CERT_LeisureHub"))
        df = pd.read_sql("""
            SELECT u.user_id, u.name, u.age_group, u.available_hours_per_week, u.account_status,
                   ISNULL(TRY_CAST(
                       REPLACE(REPLACE(LTRIM(RTRIM(
                           CONVERT(VARCHAR(50), DECRYPTBYKEY(u.monthly_budget_encrypted))
                       )), CHAR(0), ''), CHAR(13), '')
                   AS DECIMAL(10,2)), 0.0) AS monthly_budget,
                   COUNT(DISTINCT r.recommendation_id) AS total_recommendations,
                   SUM(CASE WHEN r.recommendation_status='clicked' THEN 1 ELSE 0 END) AS clicked_recommendations,
                   COUNT(DISTINCT uf.feedback_id) AS total_feedbacks,
                   ISNULL(AVG(CAST(uf.rating AS DECIMAL(3,1))), 0) AS avg_rating_given,
                   SUM(CASE WHEN uf.completion_status='Completed' THEN 1 ELSE 0 END) AS completed_items,
                   COUNT(DISTINCT si.saved_item_id) AS saved_items_count,
                   COUNT(DISTINCT ua.user_activity_id) AS activities_tracked,
                   SUM(CASE WHEN ua.progress_status='Completed' THEN 1 ELSE 0 END) AS activities_completed,
                   ISNULL(AVG(CAST(ua.difficulty_rating AS DECIMAL(3,1))), 0) AS avg_difficulty_rating
            FROM USERS u
            LEFT JOIN RECOMMENDATIONS r  ON r.user_id  = u.user_id
            LEFT JOIN USER_FEEDBACK   uf ON uf.user_id = u.user_id
            LEFT JOIN SAVED_ITEMS     si ON si.user_id = u.user_id
            LEFT JOIN USER_ACTIVITY   ua ON ua.user_id = u.user_id
            GROUP BY u.user_id, u.name, u.age_group, u.available_hours_per_week,
                     u.account_status, u.monthly_budget_encrypted
        """, conn)
        conn.execute(text("CLOSE SYMMETRIC KEY SYMKEY_LeisureHub"))
    return df

@st.cache_data(ttl=300)
def load_recommendations():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT r.recommendation_id, u.name AS user_name, u.age_group,
                   c.title AS content_title, c.content_type,
                   cat.category_name, r.recommendation_status, r.recommended_at, r.viewed_at
            FROM RECOMMENDATIONS r
            JOIN USERS      u   ON u.user_id       = r.user_id
            JOIN CONTENT    c   ON c.content_id    = r.content_id
            JOIN CATEGORIES cat ON cat.category_id = c.category_id
        """, conn)

@st.cache_data(ttl=300)
def load_effectiveness():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT c.content_id, c.title, c.content_type, cat.category_name,
                   COUNT(r.recommendation_id) AS times_recommended,
                   SUM(CASE WHEN r.recommendation_status='served'    THEN 1 ELSE 0 END) AS served_count,
                   SUM(CASE WHEN r.recommendation_status='viewed'    THEN 1 ELSE 0 END) AS viewed_count,
                   SUM(CASE WHEN r.recommendation_status='clicked'   THEN 1 ELSE 0 END) AS clicked_count,
                   SUM(CASE WHEN r.recommendation_status='dismissed' THEN 1 ELSE 0 END) AS dismissed_count,
                   CASE WHEN COUNT(r.recommendation_id)=0 THEN 0
                        ELSE CAST(SUM(CASE WHEN r.recommendation_status='clicked' THEN 1 ELSE 0 END) AS DECIMAL(5,2))
                             / COUNT(r.recommendation_id) * 100
                   END AS click_through_rate_pct,
                   ISNULL(AVG(CAST(uf.rating AS DECIMAL(3,1))), 0) AS avg_user_rating,
                   COUNT(DISTINCT uf.feedback_id) AS total_ratings
            FROM CONTENT c
            JOIN CATEGORIES   cat ON cat.category_id = c.category_id
            LEFT JOIN RECOMMENDATIONS r  ON r.content_id  = c.content_id
            LEFT JOIN USER_FEEDBACK   uf ON uf.content_id = c.content_id
            GROUP BY c.content_id, c.title, c.content_type, cat.category_name
        """, conn)

@st.cache_data(ttl=300)
def load_content():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT c.content_id, c.content_type, c.title, c.genre, cat.category_name,
                   a.activity_type, a.estimated_cost, a.time_required_hours, a.difficulty_level,
                   b.author, b.publication_year,
                   m.platform, m.imdb_rating, m.release_year,
                   p.host, p.frequency, p.total_episodes
            FROM CONTENT c
            JOIN CATEGORIES cat ON cat.category_id = c.category_id
            LEFT JOIN ACTIVITIES a ON a.activity_id = c.content_id
            LEFT JOIN BOOKS      b ON b.book_id     = c.content_id
            LEFT JOIN MOVIES     m ON m.movie_id    = c.content_id
            LEFT JOIN PODCASTS   p ON p.podcast_id  = c.content_id
        """, conn)

@st.cache_data(ttl=300)
def load_tags():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT c.content_id, c.title, c.content_type, t.tag_name, t.tag_type
            FROM CONTENT_TAGS ct
            JOIN CONTENT c ON c.content_id = ct.content_id
            JOIN TAGS    t ON t.tag_id     = ct.tag_id
        """, conn)

@st.cache_data(ttl=300)
def load_feedback():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT uf.feedback_id, u.name AS user_name, u.age_group,
                   c.title AS content_title, c.content_type,
                   uf.rating, uf.comment, uf.completion_status, uf.created_at
            FROM USER_FEEDBACK uf
            JOIN USERS   u ON u.user_id    = uf.user_id
            JOIN CONTENT c ON c.content_id = uf.content_id
        """, conn)

@st.cache_data(ttl=300)
def load_activity():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT ua.user_activity_id, u.name AS user_name, u.age_group,
                   c.title AS activity_title, a.activity_type, a.difficulty_level,
                   a.estimated_cost, a.time_required_hours AS estimated_hours,
                   ua.progress_status, ua.difficulty_rating, ua.time_taken_hours,
                   ua.started_at, ua.completed_at
            FROM USER_ACTIVITY ua
            JOIN USERS      u ON u.user_id     = ua.user_id
            JOIN ACTIVITIES a ON a.activity_id = ua.activity_id
            JOIN CONTENT    c ON c.content_id  = ua.activity_id
        """, conn)

@st.cache_data(ttl=300)
def load_saved():
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT si.saved_item_id, u.name AS user_name, u.age_group,
                   c.title AS content_title, c.content_type,
                   cat.category_name, si.save_reason, si.saved_at
            FROM SAVED_ITEMS si
            JOIN USERS      u   ON u.user_id       = si.user_id
            JOIN CONTENT    c   ON c.content_id    = si.content_id
            JOIN CATEGORIES cat ON cat.category_id = c.category_id
        """, conn)

# ── Load data ────────────────────────────────────────────────────────────────
try:
    users         = load_users()
    engagement    = load_engagement()
    recs          = load_recommendations()
    effectiveness = load_effectiveness()
    content       = load_content()
    tags          = load_tags()
    feedback      = load_feedback()
    activity      = load_activity()
    saved         = load_saved()
except Exception as e:
    st.error(f"Database connection failed: {e}")
    st.stop()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1.25rem;display:flex;align-items:center;gap:10px;'>
        <div style='width:32px;height:32px;border-radius:8px;flex-shrink:0;
            background:linear-gradient(135deg,#4f7cff,#00c9a7);
            display:flex;align-items:center;justify-content:center;'>
            <div style='width:10px;height:10px;border-radius:50%;background:#fff;opacity:0.9;'></div>
        </div>
        <div>
            <div style='font-size:18px;font-weight:700;color:#fff;letter-spacing:-0.3px;line-height:1.2;'>LeisureHub</div>
            <div style='font-size:10px;color:#4a5568;font-weight:500;letter-spacing:0.5px;'>
                ANALYTICS · DAMG 6210 · GROUP 6
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown('<div class="nav-section">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("nav", [
        "Executive Summary", "User Engagement",
        "Recommendations", "Content Catalog", "Data Manager",
    ], label_visibility="collapsed")

    st.divider()
    st.markdown('<div class="nav-section">Filters</div>', unsafe_allow_html=True)

    all_ages   = sorted(users["age_group"].unique().tolist())
    all_types  = sorted(content["content_type"].unique().tolist())
    all_status = sorted(users["account_status"].unique().tolist())

    st.markdown("<p style='font-size:12px;color:#c8cfe0;margin:8px 0 2px;'>Age group</p>", unsafe_allow_html=True)
    age_filter = st.multiselect("a", all_ages, default=all_ages, label_visibility="collapsed")
    st.markdown("<p style='font-size:12px;color:#c8cfe0;margin:8px 0 2px;'>Content type</p>", unsafe_allow_html=True)
    type_filter = st.multiselect("b", all_types, default=all_types, label_visibility="collapsed")
    st.markdown("<p style='font-size:12px;color:#c8cfe0;margin:8px 0 2px;'>Account status</p>", unsafe_allow_html=True)
    status_filter = st.multiselect("c", all_status, default=all_status, label_visibility="collapsed")

    st.divider()
    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    n_users = len(users[users["account_status"].isin(status_filter)])
    st.markdown(f"<p style='font-size:11px;color:#4a5568;margin-top:4px;'>{n_users} users in filter</p>",
                unsafe_allow_html=True)

# ── Apply filters ────────────────────────────────────────────────────────────
users_f      = users[users["age_group"].isin(age_filter) & users["account_status"].isin(status_filter)]
engagement_f = engagement[engagement["age_group"].isin(age_filter) & engagement["account_status"].isin(status_filter)]
content_f    = content[content["content_type"].isin(type_filter)]
recs_f       = recs[recs["age_group"].isin(age_filter) & recs["content_type"].isin(type_filter)]
eff_f        = effectiveness[effectiveness["content_type"].isin(type_filter)]
feedback_f   = feedback[feedback["age_group"].isin(age_filter) & feedback["content_type"].isin(type_filter)]
activity_f   = activity[activity["age_group"].isin(age_filter)]
saved_f      = saved[saved["age_group"].isin(age_filter) & saved["content_type"].isin(type_filter)]
tags_f       = tags[tags["content_type"].isin(type_filter)]

# ── Shared Plotly layout ─────────────────────────────────────────────────────
LAYOUT = dict(
    paper_bgcolor=PLOT_BG, plot_bgcolor=PLOT_BG,
    font=dict(family="Inter, sans-serif", size=12, color=FONT_COLOR),
    legend=dict(font=dict(color=FONT_COLOR), bgcolor="rgba(0,0,0,0)"),
    margin=dict(t=10, b=10, l=10, r=10),
    xaxis=dict(tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR),
               gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(tickfont=dict(color=FONT_COLOR), title_font=dict(color=FONT_COLOR),
               gridcolor=GRID_COLOR, linecolor=AXIS_COLOR, zerolinecolor=GRID_COLOR),
)

CHART_CFG = {
    "displayModeBar": True, "displaylogo": False,
    "modeBarButtonsToRemove": ["select2d", "lasso2d", "autoScale2d"],
    "toImageButtonOptions": {"format": "png", "filename": "leisurehub_chart", "scale": 2},
}

def use_cw():
    import streamlit as _st
    ver = tuple(int(x) for x in _st.__version__.split(".")[:2])
    return {"width": "stretch"} if ver >= (1, 45) else {"use_container_width": True}

def show_alerts():
    if "alert" in st.session_state:
        kind, msg = st.session_state.pop("alert")
        if kind == "success":
            st.success(msg)
        else:
            st.error(msg)

def set_alert(kind, msg, tab="Users"):
    st.session_state["alert"]    = (kind, msg)
    st.session_state["crud_tab"] = tab
    st.cache_data.clear()
    st.rerun()

def kpi(label, value, icon=""):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
    </div>""", unsafe_allow_html=True)

def chart(title, fig, height=320):
    fig.update_layout(height=height, **LAYOUT)
    for trace in fig.data:
        if hasattr(trace, "textfont") and trace.textfont:
            trace.textfont.color = FONT_COLOR
    st.markdown(f'<div class="chart-card"><div class="chart-title">{title}</div></div>',
                unsafe_allow_html=True)
    st.plotly_chart(fig, config=CHART_CFG, **use_cw())

def insight(text, icon=""):
    st.markdown(f'<div class="insight-box"><span class="insight-icon">{icon}</span><span>{text}</span></div>',
                unsafe_allow_html=True)

def section(label):
    st.markdown(f'<div class="section-label">{label}</div>', unsafe_allow_html=True)

def page_header(title, subtitle):
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{title}</div>
        <div class="page-subtitle">{subtitle}</div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Executive Summary
# ════════════════════════════════════════════════════════════════════════════
if page == "Executive Summary":
    page_header("Executive Summary", "Platform-wide health metrics across all users and content")

    active  = len(users_f[users_f["account_status"] == "active"])
    total_c = len(content_f)
    avg_r   = round(feedback_f["rating"].mean(), 1) if len(feedback_f) else 0
    ctr     = round(eff_f["click_through_rate_pct"].mean(), 1) if len(eff_f) else 0
    n_recs  = len(recs_f)
    comps   = int(engagement_f["completed_items"].sum())

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi("Active users",    active)
    with c2: kpi("Content items",   total_c)
    with c3: kpi("Avg rating",      f"{avg_r} *")
    with c4: kpi("Avg CTR",         f"{ctr}%")
    with c5: kpi("Recommendations", n_recs)
    with c6: kpi("Completions",     comps)

    section("Engagement Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        sc = recs_f["recommendation_status"].value_counts().reset_index()
        sc.columns = ["status", "count"]
        fig_a = px.pie(sc, names="status", values="count", hole=0.55, color_discrete_sequence=COLORS)
        fig_a.update_traces(textposition="outside", textinfo="percent+label", textfont=dict(color=FONT_COLOR))
        fig_a.update_layout(showlegend=False)
        chart("Recommendation status", fig_a, 280)
    with col2:
        ac = users_f["age_group"].value_counts().reset_index()
        ac.columns = ["age_group", "count"]
        fig_b = px.bar(ac, x="age_group", y="count", color="age_group",
                       color_discrete_sequence=COLORS, text="count")
        fig_b.update_traces(textposition="outside", textfont=dict(color=FONT_COLOR))
        fig_b.update_layout(showlegend=False, xaxis_title="", yaxis_title="Users")
        chart("Users by age group", fig_b, 280)
    with col3:
        tc = content_f["content_type"].value_counts().reset_index()
        tc.columns = ["type", "count"]
        fig_c = px.pie(tc, names="type", values="count", color_discrete_sequence=COLORS)
        fig_c.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(color="#ffffff"))
        fig_c.update_layout(showlegend=False)
        chart("Content by type", fig_c, 280)

    section("Content Landscape")
    col4, col5 = st.columns([3, 2])
    with col4:
        fig_d = px.sunburst(content_f, path=["content_type", "category_name"],
                            color="content_type", color_discrete_sequence=COLORS)
        fig_d.update_traces(textfont=dict(color="#ffffff"))
        chart("Content hierarchy — type to category", fig_d, 380)
    with col5:
        fig_e = px.histogram(feedback_f, x="rating", nbins=5, color_discrete_sequence=[COLORS[0]])
        fig_e.update_layout(xaxis_title="Rating", yaxis_title="Count", bargap=0.15)
        chart("Rating distribution", fig_e, 185)
        top_cat = content_f["category_name"].value_counts().head(5).reset_index()
        top_cat.columns = ["category", "count"]
        fig_f = px.bar(top_cat, x="count", y="category", orientation="h",
                       color_discrete_sequence=[COLORS[1]], text="count")
        fig_f.update_traces(textposition="outside", textfont=dict(color=FONT_COLOR))
        fig_f.update_layout(showlegend=False, xaxis_title="", yaxis_title="")
        chart("Top categories", fig_f, 185)

    section("Key Insights")
    if len(users_f):
        insight(f"<b>{users_f['age_group'].value_counts().idxmax()}</b> is the largest user demographic.")
    if len(recs_f):
        insight(f"<b>{recs_f['content_type'].value_counts().idxmax().title()}s</b> receive the most recommendations.")
    if avg_r >= 4:
        insight(f"Platform avg rating of <b>{avg_r}</b> reflects strong user satisfaction.")
    if ctr > 0:
        insight(f"<b>{ctr}%</b> average click-through rate across all recommendations.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — User Engagement
# ════════════════════════════════════════════════════════════════════════════
elif page == "User Engagement":
    page_header("User Engagement", "How users interact with content across the platform")

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Feedbacks",       len(feedback_f))
    with c2: kpi("Avg rating",      f"{round(engagement_f['avg_rating_given'].mean(), 1)}" if len(engagement_f) else "-")
    with c3: kpi("Activities done", int(engagement_f["activities_completed"].sum()))
    with c4: kpi("Items saved",     int(engagement_f["saved_items_count"].sum()))
    with c5:
        diff_val = round(activity_f["difficulty_rating"].mean(), 1) if len(activity_f) and activity_f["difficulty_rating"].notna().any() else "-"
        kpi("Avg difficulty", f"{diff_val}/5")

    section("Ratings & Activity")
    col1, col2 = st.columns(2)
    with col1:
        avg_age = engagement_f.groupby("age_group")["avg_rating_given"].mean().reset_index()
        fig_a = px.bar(avg_age, x="avg_rating_given", y="age_group", orientation="h",
                       color="age_group", color_discrete_sequence=COLORS, text=avg_age["avg_rating_given"].round(2))
        fig_a.update_traces(texttemplate="%{text:.1f}", textposition="outside", textfont=dict(color=FONT_COLOR))
        fig_a.update_layout(showlegend=False, xaxis=dict(range=[0,5]), xaxis_title="Avg Rating", yaxis_title="")
        chart("Avg rating by age group", fig_a)
    with col2:
        sc = activity_f["progress_status"].value_counts().reset_index()
        sc.columns = ["status", "count"]
        cmap = {"Completed":"#00c9a7","In Progress":"#4f7cff","Started":"#ffa94d","Paused":"#a29bfe","Not Started":"#6b7280"}
        fig_b = px.bar(sc, x="count", y="status", orientation="h", color="status",
                       color_discrete_map=cmap, text="count")
        fig_b.update_traces(textposition="outside", textfont=dict(color=FONT_COLOR))
        fig_b.update_layout(showlegend=False, xaxis_title="Count", yaxis_title="")
        chart("Activity progress status", fig_b)

    section("Per-User Breakdown")
    col3, col4 = st.columns(2)
    with col3:
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(name="Completed", x=engagement_f["name"], y=engagement_f["completed_items"],    marker_color=COLORS[0]))
        fig_c.add_trace(go.Bar(name="Saved",     x=engagement_f["name"], y=engagement_f["saved_items_count"], marker_color=COLORS[1]))
        fig_c.add_trace(go.Bar(name="Feedbacks", x=engagement_f["name"], y=engagement_f["total_feedbacks"],   marker_color=COLORS[2]))
        fig_c.update_layout(barmode="group", xaxis_title="", yaxis_title="Count",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        chart("Engagement breakdown per user", fig_c)
    with col4:
        if len(activity_f) and activity_f["difficulty_rating"].notna().any():
            da = activity_f.groupby("activity_title")["difficulty_rating"].mean().reset_index()
            da.columns = ["activity", "avg_difficulty"]
            da = da.sort_values("avg_difficulty", ascending=True)
            fig_d = px.bar(da, x="avg_difficulty", y="activity", orientation="h",
                           color="avg_difficulty", color_continuous_scale="RdYlGn_r",
                           range_x=[0,5], text=da["avg_difficulty"].round(1))
            fig_d.update_traces(textposition="outside", textfont=dict(color=FONT_COLOR))
            fig_d.update_layout(showlegend=False, coloraxis_showscale=False,
                                xaxis_title="Avg difficulty (1=Easy, 5=Hard)", yaxis_title="")
            chart("Difficulty rating by activity", fig_d)

    section("User Profiles")
    fig_e = px.scatter(users_f, x="available_hours_per_week", y="monthly_budget",
                       color="age_group", size_max=20, hover_data=["name","account_status"],
                       color_discrete_sequence=COLORS,
                       labels={"available_hours_per_week":"Hours / week","monthly_budget":"Monthly budget ($)"})
    fig_e.update_traces(marker=dict(size=14, opacity=0.8, line=dict(width=1.5, color="rgba(255,255,255,0.4)")))
    chart("Budget vs available hours by age group", fig_e, 340)

    section("Leaderboard")
    lb = engagement_f[["name","age_group","total_recommendations","avg_rating_given",
                        "completed_items","saved_items_count","activities_completed"]]
    lb = lb.rename(columns={"name":"User","age_group":"Age Group","total_recommendations":"Recs Received",
                             "avg_rating_given":"Avg Rating","completed_items":"Items Completed",
                             "saved_items_count":"Items Saved","activities_completed":"Activities Done"
                             }).sort_values("Items Completed", ascending=False)
    st.dataframe(lb, hide_index=True, **use_cw(),
                 column_config={"Avg Rating": st.column_config.NumberColumn(format="%.1f")})

    section("Key Insights")
    if len(engagement_f):
        top_user = engagement_f.loc[engagement_f["completed_items"].idxmax(), "name"]
        insight(f"<b>{top_user}</b> leads the platform in completed items.")
    if len(activity_f) and activity_f["difficulty_rating"].notna().any():
        easiest = activity_f.groupby("activity_title")["difficulty_rating"].mean().idxmin()
        hardest = activity_f.groupby("activity_title")["difficulty_rating"].mean().idxmax()
        insight(f"Users found <b>{easiest}</b> the easiest and <b>{hardest}</b> the hardest activity.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Recommendations
# ════════════════════════════════════════════════════════════════════════════
elif page == "Recommendations":
    page_header("Recommendation Effectiveness", "How well the engine drives user action")

    total   = len(recs_f)
    clicked = len(recs_f[recs_f["recommendation_status"] == "clicked"])
    viewed  = len(recs_f[recs_f["recommendation_status"] == "viewed"])
    dis     = len(recs_f[recs_f["recommendation_status"] == "dismissed"])
    served  = len(recs_f[recs_f["recommendation_status"] == "served"])
    ctr     = round(clicked / total * 100, 1) if total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: kpi("Total recs", total)
    with c2: kpi("Clicked",    clicked)
    with c3: kpi("Viewed",     viewed)
    with c4: kpi("Dismissed",  dis)
    with c5: kpi("CTR",        f"{ctr}%")

    section("Funnel & Performance")
    col1, col2 = st.columns(2)
    with col1:
        ordered = ["served","viewed","clicked","dismissed"]
        fvals   = [len(recs_f[recs_f["recommendation_status"] == s]) for s in ordered]
        fig_a = go.Figure(go.Funnel(y=ordered, x=fvals, textinfo="value+percent initial",
                                    textfont=dict(color=FONT_COLOR),
                                    marker=dict(color=COLORS[:4], line=dict(width=1, color="rgba(255,255,255,0.15)"))))
        chart("Recommendation funnel", fig_a, 320)
    with col2:
        ct = eff_f.groupby("content_type")["click_through_rate_pct"].mean().reset_index()
        fig_b = px.bar(ct, x="click_through_rate_pct", y="content_type", orientation="h",
                       color="content_type", color_discrete_sequence=COLORS, text=ct["click_through_rate_pct"].round(1))
        fig_b.update_traces(texttemplate="%{text:.1f}%", textposition="outside", textfont=dict(color=FONT_COLOR))
        fig_b.update_layout(showlegend=False, xaxis_title="CTR %", yaxis_title="")
        chart("Click-through rate by content type", fig_b, 320)

    section("Category Analysis")
    col3, col4 = st.columns(2)
    with col3:
        ce = eff_f.groupby("category_name")[["clicked_count","viewed_count","dismissed_count"]].sum().reset_index()
        fig_c = go.Figure()
        fig_c.add_trace(go.Bar(name="Clicked",   x=ce["category_name"], y=ce["clicked_count"],   marker_color=COLORS[0]))
        fig_c.add_trace(go.Bar(name="Viewed",    x=ce["category_name"], y=ce["viewed_count"],    marker_color=COLORS[1]))
        fig_c.add_trace(go.Bar(name="Dismissed", x=ce["category_name"], y=ce["dismissed_count"], marker_color=COLORS[2]))
        fig_c.update_layout(barmode="group", xaxis_title="", yaxis_title="Count",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02))
        chart("Engagement by category", fig_c, 320)
    with col4:
        sc2 = eff_f[eff_f["times_recommended"] > 0]
        fig_d = px.scatter(sc2, x="times_recommended", y="click_through_rate_pct",
                           size="avg_user_rating", color="content_type", hover_name="title",
                           color_discrete_sequence=COLORS,
                           labels={"times_recommended":"Times recommended","click_through_rate_pct":"CTR %","avg_user_rating":"Avg rating"})
        fig_d.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="rgba(255,255,255,0.3)")))
        chart("CTR vs frequency (bubble = avg rating)", fig_d, 320)

    section("Content Effectiveness")
    st.dataframe(
        eff_f[["title","content_type","category_name","times_recommended","clicked_count","dismissed_count","avg_user_rating","click_through_rate_pct"]]
        .sort_values("click_through_rate_pct", ascending=False)
        .rename(columns={"title":"Title","content_type":"Type","category_name":"Category",
                         "times_recommended":"Recommended","clicked_count":"Clicked",
                         "dismissed_count":"Dismissed","avg_user_rating":"Avg Rating","click_through_rate_pct":"CTR %"}),
        hide_index=True, **use_cw(),
        column_config={"CTR %": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
                       "Avg Rating": st.column_config.NumberColumn(format="%.1f")})

    section("Key Insights")
    if len(eff_f) and eff_f["click_through_rate_pct"].max() > 0:
        insight(f"<b>{eff_f.loc[eff_f['click_through_rate_pct'].idxmax(), 'title']}</b> has the highest click-through rate.")
    if dis > 0 and len(recs_f):
        top_dis = recs_f[recs_f["recommendation_status"]=="dismissed"]["category_name"].value_counts().idxmax()
        insight(f"Dismissed recommendations cluster most in <b>{top_dis}</b>.")
    if served > 0:
        insight(f"<b>{served}</b> recommendations are still unviewed — re-engagement opportunity.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Content Catalog
# ════════════════════════════════════════════════════════════════════════════
elif page == "Content Catalog":
    page_header("Content Catalog", "Full overview of the LeisureHub content library")

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Total content",   len(content_f))
    with c2: kpi("Categories",      content_f["category_name"].nunique())
    with c3: kpi("Unique tags",     tags_f["tag_name"].nunique())
    with c4: kpi("Tag assignments", len(tags_f))

    section("Library Overview")
    col1, col2 = st.columns(2)
    with col1:
        fig_a = px.treemap(content_f, path=["content_type","category_name"],
                           color="content_type", color_discrete_sequence=COLORS)
        fig_a.update_traces(textfont=dict(color="#ffffff"))
        chart("Content hierarchy", fig_a, 360)
    with col2:
        tc = tags_f["tag_name"].value_counts().head(12).reset_index()
        tc.columns = ["tag","count"]
        fig_b = px.bar(tc, x="count", y="tag", orientation="h",
                       color="count", color_continuous_scale="Blues", text="count")
        fig_b.update_traces(textposition="outside", textfont=dict(color=FONT_COLOR))
        fig_b.update_layout(coloraxis_showscale=False, xaxis_title="Assignments", yaxis_title="")
        chart("Top 12 tags by usage", fig_b, 360)

    section("Type Deep-Dives")
    col3, col4, col5, col6 = st.columns(4)
    with col3:
        acts = content_f[content_f["content_type"]=="activity"].dropna(subset=["difficulty_level"])
        if len(acts):
            dc = acts["difficulty_level"].value_counts().reset_index()
            dc.columns = ["difficulty","count"]
            fig_c = px.pie(dc, names="difficulty", values="count", hole=0.5,
                           color="difficulty", color_discrete_map={"Beginner":"#00c9a7","Intermediate":"#ffa94d","Advanced":"#ff6b6b"})
            fig_c.update_traces(textposition="outside", textinfo="percent+label", textfont=dict(color=FONT_COLOR))
            fig_c.update_layout(showlegend=False)
            chart("Activity difficulty", fig_c, 260)
    with col4:
        movies = content_f[content_f["content_type"]=="movie"].dropna(subset=["imdb_rating"])
        if len(movies):
            fig_d = px.histogram(movies, x="imdb_rating", nbins=8, color_discrete_sequence=[COLORS[3]])
            fig_d.update_layout(xaxis_title="IMDb Rating", yaxis_title="Count", bargap=0.1)
            chart("IMDb ratings", fig_d, 260)
    with col5:
        ttc = tags_f["tag_type"].value_counts().reset_index()
        ttc.columns = ["tag_type","count"]
        fig_e = px.pie(ttc, names="tag_type", values="count", color_discrete_sequence=COLORS, hole=0.4)
        fig_e.update_traces(textposition="outside", textinfo="percent+label", textfont=dict(color=FONT_COLOR))
        fig_e.update_layout(showlegend=False)
        chart("Tag types", fig_e, 260)
    with col6:
        pod = content_f[content_f["content_type"]=="podcast"].dropna(subset=["frequency"])
        if len(pod):
            fc = pod["frequency"].value_counts().reset_index()
            fc.columns = ["frequency","count"]
            fig_f = px.pie(fc, names="frequency", values="count", color_discrete_sequence=COLORS, hole=0.4)
            fig_f.update_traces(textposition="outside", textinfo="percent+label", textfont=dict(color=FONT_COLOR))
            fig_f.update_layout(showlegend=False)
            chart("Podcast frequency", fig_f, 260)

    section("Full Content Library")
    st.dataframe(
        content_f[["title","content_type","category_name","genre","difficulty_level","imdb_rating","author","platform","host"]]
        .sort_values("content_type")
        .rename(columns={"title":"Title","content_type":"Type","category_name":"Category","genre":"Genre",
                         "difficulty_level":"Difficulty","imdb_rating":"IMDb","author":"Author","platform":"Platform","host":"Host"}),
        hide_index=True, **use_cw(),
        column_config={"IMDb": st.column_config.NumberColumn(format="%.1f")})

    section("Key Insights")
    if len(tags_f):
        insight(f"<b>{tags_f['tag_name'].value_counts().idxmax()}</b> is the most frequently assigned tag.")
    if len(content_f):
        insight(f"<b>{content_f['category_name'].value_counts().idxmax()}</b> has the most content items.")
        acts_pct = round(len(content_f[content_f["content_type"]=="activity"]) / len(content_f) * 100)
        insight(f"Activities make up <b>{acts_pct}%</b> of total content.")

# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Data Manager (CRUD)
# ════════════════════════════════════════════════════════════════════════════
elif page == "Data Manager":
    page_header("Data Manager", "Create, view, update and delete records directly from the dashboard")
    show_alerts()

    # Fresh loaders — ttl=0 means never cache, always hit DB
    def fresh_users():
        with engine.connect() as conn:
            conn.execute(text("OPEN SYMMETRIC KEY SYMKEY_LeisureHub DECRYPTION BY CERTIFICATE CERT_LeisureHub"))
            df = pd.read_sql("""
                SELECT user_id, name, age_group,
                       ISNULL(TRY_CAST(
                           REPLACE(REPLACE(LTRIM(RTRIM(
                               CONVERT(VARCHAR(50), DECRYPTBYKEY(monthly_budget_encrypted))
                           )), CHAR(0), ''), CHAR(13), '')
                       AS DECIMAL(10,2)), 0.0) AS monthly_budget,
                       available_hours_per_week, account_status, created_at
                FROM USERS
            """, conn)
            conn.execute(text("CLOSE SYMMETRIC KEY SYMKEY_LeisureHub"))
        return df

    def fresh_content():
        with engine.connect() as conn:
            return pd.read_sql("""
                SELECT c.content_id, c.content_type, c.title, c.genre,
                       ISNULL(c.description,'') AS description, cat.category_name
                FROM CONTENT c
                JOIN CATEGORIES cat ON cat.category_id = c.category_id
            """, conn)

    def fresh_recs():
        with engine.connect() as conn:
            return pd.read_sql("""
                SELECT r.recommendation_id, u.name AS user_name,
                       c.title AS content_title, c.content_type,
                       r.recommendation_status, r.recommended_at
                FROM RECOMMENDATIONS r
                JOIN USERS   u ON u.user_id    = r.user_id
                JOIN CONTENT c ON c.content_id = r.content_id
            """, conn)

    def fresh_feedback():
        with engine.connect() as conn:
            return pd.read_sql("""
                SELECT uf.feedback_id, u.name AS user_name,
                       c.title AS content_title, c.content_type,
                       uf.rating, uf.completion_status, uf.comment, uf.created_at
                FROM USER_FEEDBACK uf
                JOIN USERS   u ON u.user_id    = uf.user_id
                JOIN CONTENT c ON c.content_id = uf.content_id
            """, conn)

    dm_users    = fresh_users()
    dm_content  = fresh_content()
    dm_recs     = fresh_recs()
    dm_feedback = fresh_feedback()

    # Tab nav via session_state — survives rerun perfectly
    if "crud_tab" not in st.session_state:
        st.session_state["crud_tab"] = "Users"

    tab_names = ["Users", "Content", "Recommendations", "Feedback"]
    sel_tab   = st.radio("crud_nav", tab_names,
                         index=tab_names.index(st.session_state["crud_tab"]),
                         horizontal=True, label_visibility="collapsed")
    st.session_state["crud_tab"] = sel_tab
    st.divider()

    # ── USERS ────────────────────────────────────────────────────────────────
    if sel_tab == "Users":
        section("All Users")
        st.dataframe(dm_users.sort_values("user_id"), hide_index=True, **use_cw())

        col_a, col_b = st.columns(2)
        with col_a:
            section("Add New User")
            with st.form("add_user"):
                u_name   = st.text_input("Full name")
                u_email  = st.text_input("Email")
                u_age    = st.selectbox("Age group", ["Teen","Young Adult","Adult","Senior"])
                u_budget = st.number_input("Monthly budget ($)", min_value=0.0, value=100.0, step=10.0)
                u_hours  = st.number_input("Available hours/week", min_value=0.0, value=10.0, step=1.0)
                u_status = st.selectbox("Account status", ["active","inactive","suspended"])
                if st.form_submit_button("Add User", use_container_width=True):
                    if not u_name or not u_email:
                        st.error("Name and email are required.")
                    else:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    OPEN SYMMETRIC KEY SYMKEY_LeisureHub
                                        DECRYPTION BY CERTIFICATE CERT_LeisureHub;
                                    INSERT INTO USERS (name, email_encrypted, monthly_budget_encrypted,
                                        age_group, available_hours_per_week, account_status)
                                    VALUES (
                                        :name,
                                        ENCRYPTBYKEY(KEY_GUID('SYMKEY_LeisureHub'), :email),
                                        ENCRYPTBYKEY(KEY_GUID('SYMKEY_LeisureHub'), :budget),
                                        :age, :hours, :status);
                                    CLOSE SYMMETRIC KEY SYMKEY_LeisureHub;
                                """), {"name":u_name, "email":u_email,
                                       "budget":f"{u_budget:.2f}",
                                       "age":u_age, "hours":u_hours, "status":u_status})
                            set_alert("success", f"User '{u_name}' added successfully.", tab="Users")
                        except Exception as e:
                            st.error(f"Error: {e}")

        with col_b:
            section("Edit User")
            user_opts = {f"{r.user_id} — {r.name}": r.user_id for r in dm_users.itertuples()}
            sel_edit  = st.selectbox("Select user", list(user_opts.keys()), key="edit_u_sel")
            sel_row   = dm_users[dm_users["user_id"] == user_opts[sel_edit]].iloc[0]
            with st.form("edit_user"):
                e_name   = st.text_input("Full name", value=str(sel_row["name"]))
                e_age    = st.selectbox("Age group", ["Teen","Young Adult","Adult","Senior"],
                                        index=["Teen","Young Adult","Adult","Senior"].index(sel_row["age_group"]))
                # Handle NaN budget safely
                current_budget = float(sel_row["monthly_budget"]) if pd.notna(sel_row["monthly_budget"]) else 0.0
                e_budget = st.number_input("Monthly budget ($)", min_value=0.0,
                                           value=current_budget, step=10.0)
                e_hours  = st.number_input("Hours/week", min_value=0.0,
                                           value=float(sel_row["available_hours_per_week"]), step=1.0)
                e_status = st.selectbox("Account status", ["active","inactive","suspended"],
                                        index=["active","inactive","suspended"].index(sel_row["account_status"]))
                if st.form_submit_button("Save Changes", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                OPEN SYMMETRIC KEY SYMKEY_LeisureHub
                                    DECRYPTION BY CERTIFICATE CERT_LeisureHub;
                                UPDATE USERS SET
                                    name=:n, age_group=:a,
                                    available_hours_per_week=:h,
                                    account_status=:s,
                                    monthly_budget_encrypted=ENCRYPTBYKEY(KEY_GUID('SYMKEY_LeisureHub'), :budget),
                                    updated_at=GETDATE()
                                WHERE user_id=:id;
                                CLOSE SYMMETRIC KEY SYMKEY_LeisureHub;
                            """), {"n":e_name, "a":e_age, "h":e_hours, "s":e_status,
                                   "budget":f"{e_budget:.2f}", "id":user_opts[sel_edit]})
                        set_alert("success", f"User '{e_name}' updated successfully.", tab="Users")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

            section("Delete User")
            with st.form("del_user"):
                del_u = st.selectbox("Select user to delete", list(user_opts.keys()), key="del_u")
                if st.form_submit_button("Delete User", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM USERS WHERE user_id=:id"), {"id":user_opts[del_u]})
                        set_alert("success", "User deleted successfully.", tab="Users")
                    except Exception as e:
                        st.error(f"Cannot delete — user may have related records. Error: {e}")

    # ── CONTENT ──────────────────────────────────────────────────────────────
    elif sel_tab == "Content":
        section("All Content")
        st.dataframe(dm_content[["content_id","content_type","title","category_name","genre"]]
                     .sort_values("content_id"), hide_index=True, **use_cw())

        cats      = {r.category_name: r.category_id for r in
                     pd.read_sql("SELECT category_id, category_name FROM CATEGORIES", engine).itertuples()}
        cat_names = list(cats.keys())
        col_a, col_b = st.columns(2)

        with col_a:
            section("Add New Content")
            with st.form("add_content"):
                c_type  = st.selectbox("Content type", ["activity","book","movie","podcast"])
                c_title = st.text_input("Title")
                c_genre = st.text_input("Genre")
                c_desc  = st.text_area("Description", height=80)
                c_cat   = st.selectbox("Category", cat_names)
                if st.form_submit_button("Add Content", use_container_width=True):
                    if not c_title:
                        st.error("Title is required.")
                    else:
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO CONTENT (content_type, title, description, category_id, genre)
                                    VALUES (:t, :ti, :d, :c, :g)
                                """), {"t":c_type,"ti":c_title,"d":c_desc,"c":cats[c_cat],"g":c_genre})
                            set_alert("success", f"'{c_title}' added successfully.", tab="Content")
                        except Exception as e:
                            st.error(f"Error: {e}")

        with col_b:
            section("Edit Content")
            cont_opts = {f"{r.content_id} — {r.title}": r.content_id for r in dm_content.itertuples()}
            sel_cont  = st.selectbox("Select content", list(cont_opts.keys()), key="edit_c_sel")
            sel_crow  = dm_content[dm_content["content_id"] == cont_opts[sel_cont]].iloc[0]
            with st.form("edit_content"):
                ec_title = st.text_input("Title",       value=str(sel_crow["title"]))
                ec_genre = st.text_input("Genre",       value=str(sel_crow["genre"] or ""))
                ec_desc  = st.text_area("Description",  value=str(sel_crow["description"] or ""), height=80)
                ec_cat   = st.selectbox("Category", cat_names,
                                        index=cat_names.index(sel_crow["category_name"])
                                        if sel_crow["category_name"] in cat_names else 0)
                if st.form_submit_button("Save Changes", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                UPDATE CONTENT SET title=:t, genre=:g, description=:d,
                                    category_id=:c, updated_at=GETDATE()
                                WHERE content_id=:id
                            """), {"t":ec_title,"g":ec_genre,"d":ec_desc,"c":cats[ec_cat],"id":cont_opts[sel_cont]})
                        set_alert("success", f"'{ec_title}' updated successfully.", tab="Content")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

            section("Delete Content")
            with st.form("del_content"):
                del_c = st.selectbox("Select content to delete", list(cont_opts.keys()), key="del_c")
                if st.form_submit_button("Delete Content", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM CONTENT WHERE content_id=:id"), {"id":cont_opts[del_c]})
                        set_alert("success", "Content deleted successfully.", tab="Content")
                    except Exception as e:
                        st.error(f"Cannot delete — content may have related records. Error: {e}")

    # ── RECOMMENDATIONS ──────────────────────────────────────────────────────
    elif sel_tab == "Recommendations":
        section("All Recommendations")
        st.dataframe(dm_recs[["recommendation_id","user_name","content_title","content_type",
                               "recommendation_status","recommended_at"]]
                     .sort_values("recommendation_id", ascending=False), hide_index=True, **use_cw())

        u_opts  = {f"{r.user_id} — {r.name}": r.user_id for r in dm_users.itertuples()}
        co_opts = {f"{r.content_id} — {r.title}": r.content_id for r in dm_content.itertuples()}
        col_a, col_b = st.columns(2)

        with col_a:
            section("Add Recommendation")
            with st.form("add_rec"):
                r_user   = st.selectbox("User",    list(u_opts.keys()))
                r_cont   = st.selectbox("Content", list(co_opts.keys()))
                r_reason = st.text_input("Reason (optional)")
                r_status = st.selectbox("Status", ["served","viewed","clicked","dismissed"])
                if st.form_submit_button("Add Recommendation", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO RECOMMENDATIONS
                                    (user_id, content_id, recommendation_reason, recommendation_status)
                                VALUES (:u, :c, :r, :s)
                            """), {"u":u_opts[r_user],"c":co_opts[r_cont],"r":r_reason,"s":r_status})
                        set_alert("success", "Recommendation added successfully.", tab="Recommendations")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col_b:
            section("Edit Recommendation")
            rec_opts = {f"{r.recommendation_id} — {r.user_name} → {r.content_title}": r.recommendation_id
                        for r in dm_recs.itertuples()}
            sel_rec  = st.selectbox("Select recommendation", list(rec_opts.keys()), key="edit_r_sel")
            sel_rrow = dm_recs[dm_recs["recommendation_id"] == rec_opts[sel_rec]].iloc[0]
            statuses = ["served","viewed","clicked","dismissed"]
            with st.form("edit_rec"):
                er_status = st.selectbox("Status", statuses,
                                         index=statuses.index(sel_rrow["recommendation_status"])
                                         if sel_rrow["recommendation_status"] in statuses else 0)
                if st.form_submit_button("Save Changes", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE RECOMMENDATIONS SET recommendation_status=:s WHERE recommendation_id=:id"),
                                         {"s":er_status,"id":rec_opts[sel_rec]})
                        set_alert("success", "Recommendation updated successfully.", tab="Recommendations")
                    except Exception as ex:
                        st.error(f"Error: {ex}")

            section("Delete Recommendation")
            with st.form("del_rec"):
                del_r = st.selectbox("Select to delete", list(rec_opts.keys()), key="del_r")
                if st.form_submit_button("Delete Recommendation", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("DELETE FROM RECOMMENDATIONS WHERE recommendation_id=:id"),
                                         {"id":rec_opts[del_r]})
                        set_alert("success", "Recommendation deleted successfully.", tab="Recommendations")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── FEEDBACK ─────────────────────────────────────────────────────────────
    elif sel_tab == "Feedback":
        section("All Feedback")
        st.dataframe(dm_feedback[["feedback_id","user_name","content_title","content_type",
                                   "rating","completion_status","created_at"]]
                     .sort_values("feedback_id", ascending=False), hide_index=True, **use_cw())

        u_opts2  = {f"{r.user_id} — {r.name}": r.user_id for r in dm_users.itertuples()}
        co_opts2 = {f"{r.content_id} — {r.title}": r.content_id for r in dm_content.itertuples()}
        col_a, col_b = st.columns(2)

        with col_a:
            section("Add Feedback")
            with st.form("add_feedback"):
                f_user    = st.selectbox("User",    list(u_opts2.keys()))
                f_cont    = st.selectbox("Content", list(co_opts2.keys()))
                f_rating  = st.slider("Rating", 1, 5, 3)
                f_status  = st.selectbox("Completion status", ["Not Started","Started","In Progress","Completed"])
                f_comment = st.text_area("Comment (optional)", height=80)
                if st.form_submit_button("Add Feedback", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                INSERT INTO USER_FEEDBACK
                                    (user_id, content_id, rating, completion_status, comment)
                                VALUES (:u, :c, :r, :s, :cm)
                            """), {"u":u_opts2[f_user],"c":co_opts2[f_cont],"r":f_rating,"s":f_status,"cm":f_comment})
                        set_alert("success", "Feedback added successfully.", tab="Feedback")
                    except Exception as e:
                        st.error(f"Error: {e}")

        with col_b:
            section("Edit Feedback")
            fb_opts  = {f"{r.feedback_id} — {r.user_name} on {r.content_title}": r.feedback_id
                        for r in dm_feedback.itertuples()}
            sel_fb   = st.selectbox("Select feedback", list(fb_opts.keys()), key="edit_fb_sel")
            sel_frow = dm_feedback[dm_feedback["feedback_id"] == fb_opts[sel_fb]].iloc[0]
            comp_opts = ["Not Started","Started","In Progress","Completed"]
            with st.form("upd_feedback"):
                new_rat     = st.slider("Rating", 1, 5, value=int(sel_frow["rating"]), key="upd_rat")
                new_stat    = st.selectbox("Completion status", comp_opts,
                                           index=comp_opts.index(sel_frow["completion_status"])
                                           if sel_frow["completion_status"] in comp_opts else 0,
                                           key="upd_stat")
                new_comment = st.text_area("Comment", value=str(sel_frow["comment"] or ""), height=80)
                if st.form_submit_button("Save Changes", use_container_width=True):
                    try:
                        with engine.begin() as conn:
                            conn.execute(text("""
                                UPDATE USER_FEEDBACK
                                SET rating=:r, completion_status=:s, comment=:cm, updated_at=GETDATE()
                                WHERE feedback_id=:id
                            """), {"r":new_rat,"s":new_stat,"cm":new_comment,"id":fb_opts[sel_fb]})
                        set_alert("success", "Feedback updated successfully.", tab="Feedback")
                    except Exception as e:
                        st.error(f"Error: {e}")