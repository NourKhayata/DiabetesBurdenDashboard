import os
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Diabetes Dashboard",
    layout="wide"
)

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
# Sidebar Filters
# -----------------------------

st.sidebar.header("Dashboard Filters")

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


# -----------------------------
# Header
# -----------------------------

st.title("Global Diabetes Burden and Treatment Outcomes Dashboard")

st.write(
    "This one-page interactive dashboard analyzes diabetes burden and treatment outcomes "
    "across selected countries, years, age groups, and gender categories. "
    "All graphs are coordinated using the filters on the left sidebar."
)

st.info(
    f"Current main indicator: **{selected_metric}**. "
    "Changing filters or the main indicator updates all graphs together."
)


# -----------------------------
# KPIs
# -----------------------------

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

kpi1.metric("Records", f"{filtered_df.shape[0]:,}")
kpi2.metric("Countries", f"{filtered_df['Country'].nunique()}")
kpi3.metric("Avg Prevalence", f"{filtered_df['Prevalence Rate (%)'].mean():.2f}%")
kpi4.metric("Avg Mortality", f"{filtered_df['Mortality Rate (%)'].mean():.2f}%")
kpi5.metric("Avg Recovery", f"{filtered_df['Recovery Rate (%)'].mean():.2f}%")

st.caption("All indicators are calculated based on the current sidebar filters.")

st.divider()


# -----------------------------
# Aggregated Data
# -----------------------------

trend_df = filtered_df.groupby("Year", as_index=False)[metric_options].mean()

country_df = filtered_df.groupby("Country", as_index=False).agg({
    "Prevalence Rate (%)": "mean",
    "Incidence Rate (%)": "mean",
    "Mortality Rate (%)": "mean",
    "Recovery Rate (%)": "mean",
    "Population Affected": "mean",
    "Healthcare Access (%)": "mean",
    "Doctors per 1000": "mean",
    "Hospital Beds per 1000": "mean"
})

country_ranked = country_df.sort_values(selected_metric, ascending=False)

age_order = ["0-18", "19-35", "36-60", "61+"]

age_df = filtered_df.groupby("Age Group", as_index=False)[selected_metric].mean()
age_df["Age Group"] = pd.Categorical(
    age_df["Age Group"],
    categories=age_order,
    ordered=True
)
age_df = age_df.sort_values("Age Group")

gender_df = filtered_df.groupby("Gender", as_index=False)[selected_metric].mean()

treatment_df = filtered_df.groupby("Treatment Type", as_index=False).agg({
    "Recovery Rate (%)": "mean",
    "Mortality Rate (%)": "mean",
    "Average Treatment Cost (USD)": "mean",
    "Healthcare Access (%)": "mean"
})


# -----------------------------
# Row 1: Trends + Map
# -----------------------------

left_col, right_col = st.columns([1.05, 1])

with left_col:
    fig_trend = px.line(
        trend_df,
        x="Year",
        y=selected_metric,
        markers=True,
        title=f"{selected_metric} Trend Over Time"
    )

    fig_trend.update_layout(
        xaxis_title="Year",
        yaxis_title=selected_metric,
        height=430,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    st.plotly_chart(fig_trend, use_container_width=True)

with right_col:
    fig_map = px.choropleth(
        country_df,
        locations="Country",
        locationmode="country names",
        color=selected_metric,
        hover_name="Country",
        hover_data={
            "Prevalence Rate (%)": ":.2f",
            "Incidence Rate (%)": ":.2f",
            "Mortality Rate (%)": ":.2f",
            "Recovery Rate (%)": ":.2f",
            "Healthcare Access (%)": ":.2f"
        },
        color_continuous_scale="Blues",
        title=f"{selected_metric} by Country"
    )

    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth"
        ),
        height=430,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    st.plotly_chart(fig_map, use_container_width=True)


# -----------------------------
# Row 2: Country Ranking + Age
# -----------------------------

left_col, right_col = st.columns([1.1, 0.9])

with left_col:
    fig_country = px.bar(
        country_ranked,
        x="Country",
        y=selected_metric,
        text=selected_metric,
        title=f"Countries Ranked by {selected_metric}"
    )

    fig_country.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_country.update_layout(
        xaxis_title="Country",
        yaxis_title=selected_metric,
        xaxis_tickangle=-45,
        height=430,
        margin=dict(l=20, r=20, t=60, b=90)
    )

    st.plotly_chart(fig_country, use_container_width=True)

with right_col:
    fig_age = px.bar(
        age_df,
        x="Age Group",
        y=selected_metric,
        text=selected_metric,
        title=f"{selected_metric} by Age Group"
    )

    fig_age.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title=selected_metric,
        height=430,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    st.plotly_chart(fig_age, use_container_width=True)


# -----------------------------
# Row 3: Gender + Treatment Outcomes
# -----------------------------

left_col, right_col = st.columns([0.85, 1.15])

with left_col:
    fig_gender = px.bar(
        gender_df,
        x="Gender",
        y=selected_metric,
        text=selected_metric,
        title=f"{selected_metric} by Gender"
    )

    fig_gender.update_traces(
        texttemplate="%{text:.2f}",
        textposition="outside"
    )

    fig_gender.update_layout(
        xaxis_title="Gender",
        yaxis_title=selected_metric,
        height=430,
        margin=dict(l=20, r=20, t=60, b=40)
    )

    st.plotly_chart(fig_gender, use_container_width=True)

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

    st.plotly_chart(fig_treatment, use_container_width=True)


# -----------------------------
# Interpretation Notes
# -----------------------------

st.divider()

note1, note2 = st.columns(2)

with note1:
    st.info(
        "Interpretation note: All graphs are coordinated through the same filters. "
        "This allows users to compare the selected diabetes indicator across time, geography, "
        "age groups, gender, and treatment outcomes on one page."
    )

with note2:
    st.warning(
        "Dataset limitation: The data is from a public Kaggle dataset. Some treatment categories, "
        "such as vaccination or surgery, may not represent standard diabetes treatment pathways. "
        "The dashboard should be interpreted as exploratory analytics, not clinical guidance."
    )


# -----------------------------
# Data Explorer
# -----------------------------

with st.expander("View and download filtered diabetes data"):
    st.dataframe(filtered_df, use_container_width=True)

    csv = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download Filtered Data",
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