import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import io

# 1. MUST BE THE FIRST COMMAND
st.set_page_config(
    page_title="Addiction Rehab Success Dashboard",
    page_icon="🏥",
    layout="wide"
)

# ==========================================
# 2. DATA LOADING & ENGINEERING
# ==========================================
@st.cache_data
def load_all_datasets():
    # --- A. GLOBAL DATA (Kaggle Student Dataset - 150 Rows) ---
    train = pd.read_csv("student_addiction_dataset_train.csv")
    test = pd.read_csv("student_addiction_dataset_test.csv")
    global_df = pd.concat([train, test], ignore_index=True).head(150)
    global_df.columns = global_df.columns.str.strip().str.replace(" ", "_")
    global_df = global_df.fillna("No")
    
    # Logic: Define Success vs Relapse for Global Data
    global_df["Rehab_Outcome"] = global_df.apply(
        lambda x: "✅ Successful Recovery" 
        if x["Withdrawal_Symptoms"] == "No" and x["Denial_and_Resistance_to_Treatment"] == "No"
        else "🚨 Relapse Risk", axis=1
    )
    # Severity Score (Sum of behavioral indicators)
    risk_cols = ['Social_Isolation', 'Financial_Issues', 'Legal_Consequences', 'Relationship_Strain', 'Risk_Taking_Behavior']
    global_df['Severity'] = global_df[risk_cols].apply(lambda x: (x == 'Yes').sum(), axis=1)

    # --- B. LOCAL DATA (DDB Philippines 2018-2024) ---
    ddb_trend_csv = """Year,Total_Admissions,New_Admissions,Readmitted_Relapse,Outpatient
2018,5447,5188,171,88
2019,5227,5119,22,86
2020,2385,1920,20,445
2021,2708,2372,28,336
2022,3865,3343,79,443
2023,5546,4425,85,1036
2024,6554,5537,111,906"""
    trend_df = pd.read_csv(io.StringIO(ddb_trend_csv))

    # Socio-Economic
    ddb_demog_csv = """Category,Percentage
Employed,58.25
Unemployed,37.53
Students,3.19
Out-of-school Youth,0.81
Pensioners,0.21"""
    demog_df = pd.read_csv(io.StringIO(ddb_demog_csv))

    # Drugs
    ddb_drug_csv = """Drug,Prevalence
Shabu (Meth),93.65
Cannabis (Marijuana),24.96
Cocaine,0.53"""
    drug_df = pd.read_csv(io.StringIO(ddb_drug_csv))

    # Age Groups (DDB Profile Data)
    ddb_age_csv = """Age_Group,Community_Rehab_Percent,TRC_Rehab_Percent
Age 18–24,12.7,22.3
Age 25–34,28.3,37.6
Age 35–44,33.9,27.9
Age 45+,25.1,11.9"""
    age_df = pd.read_csv(io.StringIO(ddb_age_csv))

    return global_df, trend_df, demog_df, drug_df, age_df

global_df, trend_df, demog_df, drug_df, age_df = load_all_datasets()

# ==========================================
# 3. SIDEBAR (Updated per request)
# ==========================================
st.sidebar.markdown("""
### 🔗 Data Sources
1. [DDB Treatment & Rehab Data](https://ddb.gov.ph/treatment-and-rehabilitation/)
2. [Kaggle Student Addiction Dataset](https://www.kaggle.com/datasets/atifmasih/students-drugs-addiction-dataset)

### 👨‍🏫 Info
**Name:**   Timothy A. Talagtag
**Yr * Sec:**   BSIT-3A 
**Instructor:**   Engr. Val Patrick Fabregas  
**Topic:**   Addiction Rehabilitation Success Metrics: Visualizing relapse vs. recovery rates in rehab centers.
""")

# ==========================================
# 4. MAIN DASHBOARD CONTENT
# ==========================================
st.title("🏥 Addiction Rehabilitation Success Metrics")
st.markdown("### Visualizing Relapse vs. Recovery Rates in Rehabilitation Centers")

tab1, tab2 = st.tabs(["🇵🇭 LOCAL INSIGHTS (DDB Philippines)", "🌏 GLOBAL BEHAVIORAL RISKS (Student Data)"])

# ------------------------------------------
# TAB 1: LOCAL INSIGHTS (DDB)
# ------------------------------------------
with tab1:
    latest = trend_df.iloc[-1]
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("National Admissions (2024)", f"{latest['Total_Admissions']:,}")
    m2.metric("New Admissions", f"{latest['New_Admissions']:,}")
    m3.metric("Relapse Cases (Readmitted)", f"{latest['Readmitted_Relapse']:,}")
    m4.metric("Entry Success Rate", f"{(latest['New_Admissions']/latest['Total_Admissions'])*100:.1f}%")

    st.divider()

    # Local Row 1
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Admission vs. Relapse Trend (2018-2024)")
        fig_line = px.line(trend_df, x="Year", y=["Total_Admissions", "Readmitted_Relapse"], 
                           markers=True, color_discrete_sequence=["#003f5c", "#ff6361"],
                           title="Longitudinal Admission Success")
        st.plotly_chart(fig_line, use_container_width=True)
    with c2:
        st.subheader("🏢 Socio-Economic Profile (2024)")
        fig_bar1 = px.bar(demog_df, x="Category", y="Percentage", color="Category", 
                          title="Employment Status of Philippine Rehabilitees")
        st.plotly_chart(fig_bar1, use_container_width=True)

    # Local Row 2
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("💊 Primary Substances of Abuse")
        fig_pie = px.pie(drug_df, names="Drug", values="Prevalence", hole=0.5,
                         title="Common Drugs Found in PH Facilities")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c4:
        st.subheader("👥 Age Group Distribution (Rehab Type)")
        fig_age = px.bar(age_df, x="Age_Group", y=["Community_Rehab_Percent", "TRC_Rehab_Percent"],
                         barmode="group", title="Age Profile: Community vs. Residential Rehab")
        st.plotly_chart(fig_age, use_container_width=True)

    # Local Row 3
    c5, c6 = st.columns([0.6, 0.4])
    with c5:
        st.subheader("📍 Regional Admission Concentration (2024)")
        # Estimates based on DDB report
        regions = pd.DataFrame({"Region": ["NCR", "Region III", "Region IV-A", "Others"], "Value": [26.6, 12.9, 11.2, 49.3]})
        fig_reg = px.bar(regions, x="Value", y="Region", orientation='h', color="Region", title="Top Admits by PH Region")
        st.plotly_chart(fig_reg, use_container_width=True)
    with c6:
        st.subheader("🏥 Treatment Setting Ratio")
        labels = ['Residential', 'Outpatient']
        values = [latest['Total_Admissions'] - latest['Outpatient'], latest['Outpatient']]
        fig_set = px.pie(names=labels, values=values, color=labels, 
                         color_discrete_map={'Residential':'#ffa600', 'Outpatient':'#bc5090'},
                         title="Residential vs. Outpatient Admissions")
        st.plotly_chart(fig_set, use_container_width=True)

# ------------------------------------------
# TAB 2: GLOBAL BEHAVIORAL RISKS
# ------------------------------------------
with tab2:
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Global Sample Size", len(global_df))
    g2.metric("High Relapse Risk", len(global_df[global_df["Rehab_Outcome"] == "🚨 Relapse Risk"]))
    g3.metric("Avg Risk Count", round(global_df["Severity"].mean(), 1))
    g4.metric("Academic Impact", f"{(global_df['Academic_Performance_Decline'] == 'Yes').mean()*100:.1f}%")

    st.divider()

    # Global Row 1
    c7, c8 = st.columns(2)
    with c7:
        st.subheader("📊 Recovery Outcome Distribution")
        fig_pie2 = px.pie(global_df, names="Rehab_Outcome", color="Rehab_Outcome", 
                          color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig_pie2, use_container_width=True)
    with c8:
        st.subheader("🧠 Denial & Resistance to Treatment")
        fig_bar2 = px.histogram(global_df, x="Denial_and_Resistance_to_Treatment", color="Rehab_Outcome", barmode="group",
                                color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig_bar2, use_container_width=True)

    # Global Row 2
    c9, c10 = st.columns(2)
    with c9:
        st.subheader("🏚️ Social Isolation & Relapse Risk")
        fig_bar3 = px.bar(global_df, x="Social_Isolation", color="Rehab_Outcome", barmode="group",
                          color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig_bar3, use_container_width=True)
    with c10:
        st.subheader("📉 Relationship Strain Frequency")
        fig_pie3 = px.pie(global_df, names="Relationship_Strain", title="Impact on Personal Relationships")
        st.plotly_chart(fig_pie3, use_container_width=True)

    # Global Row 3
    c11, c12 = st.columns(2)
    with c11:
        st.subheader("💸 Financial Issues vs. Recovery")
        fig_bar4 = px.histogram(global_df, x="Financial_Issues", color="Rehab_Outcome", barmode="group",
                                color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig_bar4, use_container_width=True)
    with c12:
        st.subheader("⚖️ Legal Consequences Count")
        fig_bar5 = px.bar(global_df, x="Legal_Consequences", color="Addiction_Class", title="Drug-Related Legal Issues")
        st.plotly_chart(fig_bar5, use_container_width=True)

    # Final Full-Width Row
    st.subheader("📈 Indicator Severity Trend")
    trend_data = global_df['Severity'].value_counts().sort_index().reset_index()
    trend_data.columns = ['Risk_Factors_Count', 'Student_Count']
    fig_line2 = px.line(trend_data, x="Risk_Factors_Count", y="Student_Count", markers=True, 
                        title="Population Density per Behavioral Risk Count")
    st.plotly_chart(fig_line2, use_container_width=True)

# ==========================================
# 5. DATA DICTIONARY (Expander)
# ==========================================
st.divider()
with st.expander("📖 View Data Dictionary & Documentation"):
    st.markdown("""
    ### Problem Statement
    To evaluate and visualize the success of addiction rehabilitation by monitoring national admission/readmission trends (relapse) and identifying the behavioral indicators that trigger recovery failures.

    ### Data Dictionary
    1. **Year:** (DDB) Annual reporting period from 2018-2024.
    2. **Readmitted_Relapse:** (DDB) Primary metric for treatment failure/relapse.
    3. **Rehab_Outcome:** (Global) Classification based on withdrawal and denial indicators.
    4. **Severity:** (Global) Sum of clinical indicators (Isolation, Finance, Legal, etc.).
    5. **Prevalence:** (DDB) Percentage of substances abused among the admitted population.
    """)