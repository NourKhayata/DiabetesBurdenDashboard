import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Diabetes Dashboard",
    layout="wide"
)

# -----------------------------
# Password Protection Landing Page
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
    df = pd.read_csv("diabetes_data.csv")
    #diabetes_df = df[df["Disease Name"] == "Diabetes"].copy()
    diabetes_df = df 
    return diabetes_df


df = load_data()


# -----------------------------
# Dashboard Header
# -----------------------------

st.title("Global Diabetes Burden and Treatment Outcomes Dashboard")

st.write(
    "This interactive dashboard analyzes diabetes burden across selected countries, "
    "years, age groups, gender categories, healthcare access indicators, and treatment outcomes. "
    "It is designed to support healthcare decision-makers in identifying high-burden groups "
    "and comparing diabetes-related outcomes across different settings."
)

st.info(
    "Use the filters on the left sidebar to explore diabetes indicators by country, year range, "
    "gender, and age group."
)


# -----------------------------
# Sidebar Filters
# -----------------------------

st.sidebar.header("Filters")

countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Select Country",
    countries,
    default=countries
)

years = sorted(df["Year"].dropna().unique())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=int(min(years)),
    max_value=int(max(years)),
    value=(int(min(years)), int(max(years)))
)

genders = sorted(df["Gender"].dropna().unique())
selected_genders = st.sidebar.multiselect(
    "Select Gender",
    genders,
    default=genders
)

age_groups = sorted(df["Age Group"].dropna().unique())
selected_age_groups = st.sidebar.multiselect(
    "Select Age Group",
    age_groups,
    default=age_groups
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
# KPI Cards
# -----------------------------

st.subheader("Key Diabetes Indicators")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Records",
    f"{filtered_df.shape[0]:,}"
)

col2.metric(
    "Avg Prevalence Rate",
    f"{filtered_df['Prevalence Rate (%)'].mean():.2f}%"
)

col3.metric(
    "Avg Mortality Rate",
    f"{filtered_df['Mortality Rate (%)'].mean():.2f}%"
)

col4.metric(
    "Avg Recovery Rate",
    f"{filtered_df['Recovery Rate (%)'].mean():.2f}%"
)

st.caption("KPIs are calculated based on the currently selected filters.")

st.divider()


# -----------------------------
# Tabs
# -----------------------------

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Trends",
    "Demographics",
    "Geography",
    "Treatment Outcomes",
    "Data Explorer"
])


# -----------------------------
# Overview Tab
# -----------------------------

with tab1:
    st.subheader("Dashboard Overview")

    st.write(
        """
        This dashboard focuses on diabetes as a global health problem. It explores:

        - Diabetes prevalence, incidence, mortality, and recovery trends over time.
        - Differences in diabetes burden by age group and gender.
        - Country-level variation in diabetes prevalence and mortality.
        - Treatment outcome patterns based on recovery rate, mortality rate, and treatment cost.
        - The relationship between diabetes outcomes and healthcare system indicators.
        """
    )

    st.subheader("Project Objective")

    st.write(
        "The objective of this dashboard is to analyze diabetes burden and treatment outcomes "
        "across selected countries and population groups in order to support data-driven "
        "healthcare planning and decision-making."
    )

    st.subheader("Data Source")

    st.write(
        "**Dataset:** Kaggle Global Health Statistics Dataset"
    )

    st.subheader("Dataset Scope")

    scope_col1, scope_col2, scope_col3 = st.columns(3)

    scope_col1.metric("Countries Included", filtered_df["Country"].nunique())
    scope_col2.metric(
        "Years Covered",
        f"{filtered_df['Year'].min()} - {filtered_df['Year'].max()}"
    )
    scope_col3.metric("Age Groups Included", filtered_df["Age Group"].nunique())

    st.warning(
        "Dataset limitation: The data is taken from a public Kaggle dataset. "
        "Some variables, especially treatment categories, may not perfectly reflect real-world "
        "clinical diabetes treatment pathways. Findings should therefore be interpreted as "
        "exploratory dashboard insights, not clinical recommendations."
    )


# -----------------------------
# Trends Tab
# -----------------------------

with tab2:
    st.subheader("Diabetes Trends Over Time")

    trend_df = filtered_df.groupby("Year", as_index=False)[
        ["Prevalence Rate (%)", "Incidence Rate (%)", "Mortality Rate (%)", "Recovery Rate (%)"]
    ].mean()

    st.write(
        "The first chart shows diabetes burden indicators over time. "
        "Recovery rate is shown separately because its values are much higher than prevalence, "
        "incidence, and mortality rates."
    )

    fig_burden = px.line(
        trend_df,
        x="Year",
        y=["Prevalence Rate (%)", "Incidence Rate (%)", "Mortality Rate (%)"],
        markers=True,
        title="Average Diabetes Burden Indicators Over Time"
    )

    fig_burden.update_layout(
        xaxis_title="Year",
        yaxis_title="Rate (%)",
        legend_title="Indicator"
    )

    st.plotly_chart(fig_burden, use_container_width=True)

    st.caption(
        "This chart compares average prevalence, incidence, and mortality rates for the selected filters."
    )

    fig_recovery = px.line(
        trend_df,
        x="Year",
        y="Recovery Rate (%)",
        markers=True,
        title="Average Diabetes Recovery Rate Over Time"
    )

    fig_recovery.update_layout(
        xaxis_title="Year",
        yaxis_title="Recovery Rate (%)"
    )

    st.plotly_chart(fig_recovery, use_container_width=True)

    st.caption(
        "Recovery rate is separated to avoid compressing the smaller burden indicators."
    )


# -----------------------------
# Demographics Tab
# -----------------------------

with tab3:
    st.subheader("Diabetes Distribution by Age Group and Gender")

    st.write(
        "This section compares average diabetes prevalence across age groups and gender categories."
    )

    age_order = ["0-18", "19-35", "36-60", "61+"]

    age_df = filtered_df.groupby("Age Group", as_index=False)["Prevalence Rate (%)"].mean()

    age_df["Age Group"] = pd.Categorical(
        age_df["Age Group"],
        categories=age_order,
        ordered=True
    )

    age_df = age_df.sort_values("Age Group")

    fig_age = px.bar(
        age_df,
        x="Age Group",
        y="Prevalence Rate (%)",
        text="Prevalence Rate (%)",
        title="Average Diabetes Prevalence by Age Group"
    )

    fig_age.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_age.update_layout(
        xaxis_title="Age Group",
        yaxis_title="Prevalence Rate (%)"
    )

    st.plotly_chart(fig_age, use_container_width=True)

    st.caption(
        "This chart helps identify which age groups show higher average diabetes prevalence."
    )

    gender_df = filtered_df.groupby("Gender", as_index=False)["Prevalence Rate (%)"].mean()

    fig_gender = px.bar(
        gender_df,
        x="Gender",
        y="Prevalence Rate (%)",
        text="Prevalence Rate (%)",
        title="Average Diabetes Prevalence by Gender"
    )

    fig_gender.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_gender.update_layout(
        xaxis_title="Gender",
        yaxis_title="Prevalence Rate (%)"
    )

    st.plotly_chart(fig_gender, use_container_width=True)

    st.caption(
        "The gender comparison is based on the gender categories available in the dataset."
    )


# -----------------------------
# Geography Tab
# -----------------------------

with tab4:
    st.subheader("Geographic Distribution")

    st.write(
        "This section compares average diabetes prevalence across the countries available in the dataset."
    )

    country_df = filtered_df.groupby("Country", as_index=False).agg({
        "Prevalence Rate (%)": "mean",
        "Mortality Rate (%)": "mean",
        "Population Affected": "mean",
        "Healthcare Access (%)": "mean",
        "Doctors per 1000": "mean",
        "Hospital Beds per 1000": "mean"
    })

    fig_map = px.choropleth(
        country_df,
        locations="Country",
        locationmode="country names",
        color="Prevalence Rate (%)",
        hover_name="Country",
        hover_data={
            "Prevalence Rate (%)": ":.2f",
            "Mortality Rate (%)": ":.2f",
            "Population Affected": ":,.0f",
            "Healthcare Access (%)": ":.2f",
            "Doctors per 1000": ":.2f",
            "Hospital Beds per 1000": ":.2f"
        },
        color_continuous_scale="Blues",
        title="Average Diabetes Prevalence by Country"
    )

    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type="natural earth"
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.caption(
        "Only countries included in the dataset appear on the map. "
        "This is a selected global sample, not a complete world diabetes surveillance dataset."
    )

    country_ranked = country_df.sort_values("Prevalence Rate (%)", ascending=False)

    fig_country = px.bar(
        country_ranked,
        x="Country",
        y="Prevalence Rate (%)",
        text="Prevalence Rate (%)",
        title="Countries Ranked by Average Diabetes Prevalence"
    )

    fig_country.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_country.update_layout(
        xaxis_title="Country",
        yaxis_title="Prevalence Rate (%)",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_country, use_container_width=True)

    st.info(
        "Interpretation note: Country-level differences in this dataset are relatively close. "
        "The ranking should be used to compare patterns, not to make strong claims that one country "
        "has a dramatically higher diabetes burden than another."
    )


# -----------------------------
# Treatment Outcomes Tab
# -----------------------------

with tab5:
    st.subheader("Treatment Outcomes")

    st.write(
        "This section explores treatment outcome indicators, including recovery rate, mortality rate, "
        "and average treatment cost."
    )

    treatment_df = filtered_df.groupby("Treatment Type", as_index=False).agg({
        "Recovery Rate (%)": "mean",
        "Mortality Rate (%)": "mean",
        "Average Treatment Cost (USD)": "mean",
        "Healthcare Access (%)": "mean"
    })

    fig_treatment = px.bar(
        treatment_df,
        x="Treatment Type",
        y="Recovery Rate (%)",
        text="Recovery Rate (%)",
        title="Average Recovery Rate by Treatment Type"
    )

    fig_treatment.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside"
    )

    fig_treatment.update_layout(
        xaxis_title="Treatment Type",
        yaxis_title="Recovery Rate (%)"
    )

    st.plotly_chart(fig_treatment, use_container_width=True)

    st.caption(
        "This chart compares recovery rates across treatment categories provided in the dataset."
    )

    fig_cost = px.scatter(
        treatment_df,
        x="Average Treatment Cost (USD)",
        y="Recovery Rate (%)",
        size="Mortality Rate (%)",
        hover_name="Treatment Type",
        hover_data={
            "Average Treatment Cost (USD)": ":,.2f",
            "Recovery Rate (%)": ":.2f",
            "Mortality Rate (%)": ":.2f",
            "Healthcare Access (%)": ":.2f"
        },
        title="Treatment Cost vs Recovery Rate"
    )

    fig_cost.update_layout(
        xaxis_title="Average Treatment Cost (USD)",
        yaxis_title="Recovery Rate (%)"
    )

    st.plotly_chart(fig_cost, use_container_width=True)

    st.warning(
        "Clinical limitation: Some treatment categories in the dataset, such as vaccination or surgery, "
        "may not represent standard diabetes treatment pathways. These variables are analyzed as dataset "
        "categories only and should not be interpreted as clinical treatment recommendations."
    )


# -----------------------------
# Data Explorer Tab
# -----------------------------

with tab6:
    st.subheader("Filtered Diabetes Data")

    st.write(
        "This table displays the diabetes records based on the selected filters. "
        "Users can download the filtered dataset for further analysis."
    )

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

st.divider()

st.markdown(
    """
    **Prepared by:** Nour Khayata  
    **Project:** MSBA382 Healthcare Analytics Individual Project  
    **Dashboard Topic:** Global Diabetes Burden and Treatment Outcomes Dashboard
    """
)