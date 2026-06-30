import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Diabetes Dashboard",
    layout="wide"
)

# Shared colour palette so that every coordinated view looks like one tool,
# not a collection of separate graphs.
SELECTED_COLOR = "#08519c"   # strong blue  -> currently selected category
MUTED_COLOR = "#c6dbef"      # light blue   -> not selected
BASE_COLOR = "#2c7fb8"       # neutral blue -> nothing selected yet
SEQ_SCALE = "Blues"

# -----------------------------
# Password Protection
# -----------------------------

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown("# Global Diabetes Burden and Treatment Outcomes Dashboard")
    st.markdown("### Please enter the password to access the dashboard.")

    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if password == "Nourdiabetes2026":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    return False


if not check_password():
    st.stop()


# -----------------------------
# Load Data
# -----------------------------

@st.cache_data
def load_data():
    if os.path.exists("diabetes_data.csv"):
        df = pd.read_csv("diabetes_data.csv")
    else:
        df = pd.read_csv("Global Health Statistics.csv")
        df = df[df["Disease Name"] == "Diabetes"].copy()

    return df


df = load_data()


# -----------------------------
# Coordination state (cross-filtering)
# -----------------------------
# These three values are the "linked selection" shared by every graph.
# Clicking any selector graph updates them, which instantly re-renders all
# the other graphs -> coordinated adjacent interactive views.

if "nonce" not in st.session_state:
    # The nonce is part of every chart key. Bumping it clears all plotly
    # selections at once (used by the Reset button).
    st.session_state.nonce = 0

NONCE = st.session_state.nonce


def read_points(key, field):
    """Read the values a user clicked on a coordinated chart."""
    state = st.session_state.get(key)
    values = []
    if state and isinstance(state, dict):
        selection = state.get("selection") or {}
        for point in selection.get("points", []):
            value = point.get(field)
            if value is not None:
                values.append(value)
    return sorted(set(values))


# Country can be selected from BOTH the map and the ranking bar, so we merge.
sel_country = sorted(set(
    read_points(f"map_{NONCE}", "location")
    + read_points(f"country_bar_{NONCE}", "x")
))
sel_age = read_points(f"age_bar_{NONCE}", "x")
sel_gender = read_points(f"gender_bar_{NONCE}", "x")


# -----------------------------
# Sidebar Filters (global context)
# -----------------------------

st.sidebar.header("Dashboard Filters")
st.sidebar.caption(
    "Sidebar filters set the global context. "
    "Click directly on the map or bars to cross-filter every graph."
)

countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Country",
    countries,
    default=countries
)

years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.slider(
    "Year range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

genders = sorted(df["Gender"].dropna().unique())
selected_genders = st.sidebar.multiselect(
    "Gender",
    genders,
    default=genders
)

age_groups = sorted(df["Age Group"].dropna().unique())
selected_age_groups = st.sidebar.multiselect(
    "Age group",
    age_groups,
    default=age_groups
)

metric_options = [
    "Prevalence Rate (%)",
    "Incidence Rate (%)",
    "Mortality Rate (%)",
    "Recovery Rate (%)"
]

selected_metric = st.sidebar.selectbox(
    "Main indicator for coordinated graphs",
    metric_options,
    index=0
)

filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["Year"].between(selected_years[0], selected_years[1])) &
    (df["Gender"].isin(selected_genders)) &
    (df["Age Group"].isin(selected_age_groups))
].copy()

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust the filters.")
    st.stop()

# Keep cross-filter clicks consistent with the sidebar context.
sel_country = [c for c in sel_country if c in selected_countries]
sel_age = [a for a in sel_age if a in selected_age_groups]
sel_gender = [g for g in sel_gender if g in selected_genders]


def apply_links(base, exclude=None):
    """Apply the shared linked selection, optionally skipping one dimension
    so a selector graph never filters itself out."""
    out = base
    if exclude != "country" and sel_country:
        out = out[out["Country"].isin(sel_country)]
    if exclude != "age" and sel_age:
        out = out[out["Age Group"].isin(sel_age)]
    if exclude != "gender" and sel_gender:
        out = out[out["Gender"].isin(sel_gender)]
    return out


# cross_df = everything the user has narrowed to -> drives KPIs + display graphs.
cross_df = apply_links(filtered_df)
if cross_df.empty:
    cross_df = filtered_df


# -----------------------------
# Header + active selection banner
# -----------------------------

st.title("Global Diabetes Burden and Treatment Outcomes Dashboard")

st.write(
    "A one-page set of **coordinated, adjacent interactive graphs**. "
    "Click a country on the map or ranking bar, an age group, or a gender on any "
    "chart and every other graph updates together (brushing & linking)."
)

banner = st.columns([4, 1])

with banner[0]:
    active_bits = []
    if sel_country:
        active_bits.append("Country: " + ", ".join(sel_country))
    if sel_age:
        active_bits.append("Age: " + ", ".join(sel_age))
    if sel_gender:
        active_bits.append("Gender: " + ", ".join(sel_gender))

    if active_bits:
        st.success(
            f"Linked selection -> {'  |  '.join(active_bits)}. "
            f"Main indicator: **{selected_metric}**."
        )
    else:
        st.info(
            f"No chart selection yet. Main indicator: **{selected_metric}**. "
            "Click any map region or bar to cross-filter all graphs."
        )

with banner[1]:
    if st.button("Reset selection", use_container_width=True):
        st.session_state.nonce += 1
        st.rerun()


# -----------------------------
# KPIs (respond to linked selection)
# -----------------------------

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Records", f"{cross_df.shape[0]:,}")
kpi2.metric("Countries", f"{cross_df['Country'].nunique()}")
kpi3.metric("Avg Prevalence", f"{cross_df['Prevalence Rate (%)'].mean():.2f}%")
kpi4.metric("Avg Mortality", f"{cross_df['Mortality Rate (%)'].mean():.2f}%")
kpi5.metric("Avg Recovery", f"{cross_df['Recovery Rate (%)'].mean():.2f}%")

st.caption("KPIs reflect the sidebar filters combined with the current chart selection.")

st.divider()


# -----------------------------
# Helper for highlighted selector bars
# -----------------------------

def bar_colors(values, selected):
    if not selected:
        return [BASE_COLOR] * len(values)
    return [SELECTED_COLOR if v in selected else MUTED_COLOR for v in values]


# -----------------------------
# Row 1: Map (country selector) + Trend (display)
# -----------------------------

map_df = apply_links(filtered_df, exclude="country").groupby(
    "Country", as_index=False
).agg({
    "Prevalence Rate (%)": "mean",
    "Incidence Rate (%)": "mean",
    "Mortality Rate (%)": "mean",
    "Recovery Rate (%)": "mean",
    "Healthcare Access (%)": "mean"
})

trend_df = cross_df.groupby("Year", as_index=False)[metric_options].mean()

left_col, right_col = st.columns([1, 1])

with left_col:
    fig_map = px.choropleth(
        map_df,
        locations="Country",
        locationmode="country names",
        color=selected_metric,
        hover_name="Country",
        hover_data={
            "Prevalence Rate (%)": ":.2f",
            "Mortality Rate (%)": ":.2f",
            "Recovery Rate (%)": ":.2f",
            "Healthcare Access (%)": ":.2f"
        },
        color_continuous_scale=SEQ_SCALE,
        title=f"{selected_metric} by Country  (click a country)"
    )
    fig_map.update_layout(
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
        height=430,
        margin=dict(l=10, r=10, t=60, b=10)
    )
    st.plotly_chart(
        fig_map,
        use_container_width=True,
        key=f"map_{NONCE}",
        on_select="rerun",
        selection_mode="points"
    )

with right_col:
    fig_trend = px.line(
        trend_df,
        x="Year",
        y=selected_metric,
        markers=True,
        title=f"{selected_metric} Trend Over Time"
    )
    fig_trend.update_traces(line_color=SELECTED_COLOR)
    fig_trend.update_layout(
        xaxis_title="Year",
        yaxis_title=selected_metric,
        height=430,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_{NONCE}")


# -----------------------------
# Row 2: Country ranking (selector) + Treatment outcomes (display)
# -----------------------------

country_rank = apply_links(filtered_df, exclude="country").groupby(
    "Country", as_index=False
)[selected_metric].mean().sort_values(selected_metric, ascending=False)

treatment_df = cross_df.groupby("Treatment Type", as_index=False).agg({
    "Recovery Rate (%)": "mean",
    "Mortality Rate (%)": "mean",
    "Average Treatment Cost (USD)": "mean",
    "Healthcare Access (%)": "mean"
})

left_col, right_col = st.columns([1, 1])

with left_col:
    fig_country = px.bar(
        country_rank,
        x="Country",
        y=selected_metric,
        title=f"Countries Ranked by {selected_metric}  (click to filter)"
    )
    fig_country.update_traces(
        marker_color=bar_colors(country_rank["Country"].tolist(), sel_country)
    )
    fig_country.update_layout(
        xaxis_title="Country",
        yaxis_title=selected_metric,
        xaxis_tickangle=-45,
        height=430,
        margin=dict(l=20, r=20, t=60, b=90)
    )
    st.plotly_chart(
        fig_country,
        use_container_width=True,
        key=f"country_bar_{NONCE}",
        on_select="rerun",
        selection_mode="points"
    )

with right_col:
    fig_treatment = px.scatter(
        treatment_df,
        x="Average Treatment Cost (USD)",
        y="Recovery Rate (%)",
        size="Mortality Rate (%)",
        color="Treatment Type",
        hover_name="Treatment Type",
        hover_data={
            "Average Treatment Cost (USD)": ":,.2f",
            "Recovery Rate (%)": ":.2f",
            "Mortality Rate (%)": ":.2f",
            "Healthcare Access (%)": ":.2f"
        },
        title="Treatment Cost vs Recovery Rate"
    )
    fig_treatment.update_layout(
        xaxis_title="Average Treatment Cost (USD)",
        yaxis_title="Recovery Rate (%)",
        height=430,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    st.plotly_chart(fig_treatment, use_container_width=True, key=f"treatment_{NONCE}")


# -----------------------------
# Row 3: Age (selector) + Gender (selector)
# -----------------------------

age_order = ["0-18", "19-35", "36-60", "61+"]

age_df = apply_links(filtered_df, exclude="age").groupby(
    "Age Group", as_index=False
)[selected_metric].mean()
age_df["Age Group"] = pd.Categorical(age_df["Age Group"], categories=age_order, ordered=True)
age_df = age_df.sort_values("Age Group")

gender_df = apply_links(filtered_df, exclude="gender").groupby(
    "Gender", as_index=False
)[selected_metric].mean()

left_col, right_col = st.columns([1, 1])

with left_col:
    fig_age = px.bar(
        age_df,
        x="Age Group",
        y=selected_metric,
        title=f"{selected_metric} by Age Group  (click to filter)"
    )
    fig_age.update_traces(
        marker_color=bar_colors(age_df["Age Group"].astype(str).tolist(), sel_age)
    )
    fig_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title=selected_metric,
        height=400,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    st.plotly_chart(
        fig_age,
        use_container_width=True,
        key=f"age_bar_{NONCE}",
        on_select="rerun",
        selection_mode="points"
    )

with right_col:
    fig_gender = px.bar(
        gender_df,
        x="Gender",
        y=selected_metric,
        title=f"{selected_metric} by Gender  (click to filter)"
    )
    fig_gender.update_traces(
        marker_color=bar_colors(gender_df["Gender"].tolist(), sel_gender)
    )
    fig_gender.update_layout(
        xaxis_title="Gender",
        yaxis_title=selected_metric,
        height=400,
        margin=dict(l=20, r=20, t=60, b=40)
    )
    st.plotly_chart(
        fig_gender,
        use_container_width=True,
        key=f"gender_bar_{NONCE}",
        on_select="rerun",
        selection_mode="points"
    )


# -----------------------------
# Interpretation Notes
# -----------------------------

st.divider()

note1, note2 = st.columns(2)

with note1:
    st.info(
        "How the views are coordinated: the map and ranking bar select countries, "
        "the age and gender bars select sub-groups, and the trend line, treatment "
        "scatter and KPIs all react to those selections at once - one linked story, "
        "not a series of independent graphs."
    )

with note2:
    st.warning(
        "Dataset limitation: The data is from a public Kaggle dataset. Some treatment "
        "categories, such as vaccination or surgery, may not represent standard diabetes "
        "treatment pathways. The dashboard should be interpreted as exploratory analytics, "
        "not clinical guidance."
    )


# -----------------------------
# Data Explorer
# -----------------------------

with st.expander("View and download the currently selected diabetes data"):
    st.dataframe(cross_df, use_container_width=True)

    csv = cross_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Selected Data",
        data=csv,
        file_name="filtered_diabetes_data.csv",
        mime="text/csv"
    )


# -----------------------------
# Footer
# -----------------------------

st.markdown(
    """
    **Prepared by:** Nour Khayata
    **Project:** MSBA382 Healthcare Analytics Individual Project
    **Dashboard Topic:** Global Diabetes Burden and Treatment Outcomes Dashboard
    """
)
