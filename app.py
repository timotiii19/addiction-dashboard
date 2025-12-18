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

    # --- B. LOCAL DATA (DDB Philippines Admissions 2018-2024) ---
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

    # Age Group Distribution
    ddb_age_csv = """Age_Group,Community_Rehab_Percent,TRC_Rehab_Percent
Age 18–24,12.7,22.3
Age 25–34,28.3,37.6
Age 35–44,33.9,27.9
Age 45+,25.1,11.9"""
    age_df = pd.read_csv(io.StringIO(ddb_age_csv))

    return global_df, trend_df, demog_df, drug_df, age_df

global_df, trend_df, demog_df, drug_df, age_df = load_all_datasets()

# ==========================================
# 3. SIDEBAR (Your Info & Sources)
# ==========================================
st.sidebar.markdown(f"""
### 🔗 Data Sources
1. [DDB Treatment & Rehab Data](https://ddb.gov.ph/treatment-and-rehabilitation/)
2. [Kaggle Student Addiction Dataset](https://www.kaggle.com/datasets/atifmasih/students-drugs-addiction-dataset)

---

### 👨‍🏫 Info
**Name:** Timothy A. Talagtag  
**Yr & Sec:** BSIT-3A  
**Instructor:** Engr. Val Patrick Fabregas  
**Topic:** Addiction Rehabilitation Success Metrics: Visualizing relapse vs. recovery rates in rehab centers.
""")

# ==========================================
# 4. MAIN DASHBOARD CONTENT
# ==========================================
st.title("🏥 Addiction Rehabilitation Success Metrics")
st.markdown("### Behavioral Diagnostics & National Recovery Trends")

tab1, tab2 = st.tabs(["🇵🇭 LOCAL INSIGHTS (DDB Philippines)", "🌏 GLOBAL BEHAVIORAL RISKS (Student Data)"])

# ------------------------------------------
# TAB 1: LOCAL (DDB PHILIPPINES) - 3x2 Layout
# ------------------------------------------
with tab1:
    latest = trend_df.iloc[-1]
    # Metrics Header
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("National Admissions (2024)", f"{latest['Total_Admissions']:,}")
    m2.metric("New Admissions", f"{latest['New_Admissions']:,}")
    m3.metric("Relapse Cases", f"{latest['Readmitted_Relapse']:,}")
    m4.metric("Entry Success Rate", f"{(latest['New_Admissions']/latest['Total_Admissions'])*100:.1f}%")

    st.divider()

    # LOCAL Row 1
    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        st.subheader("📈 Admission vs. Relapse Trend")
        fig1 = px.line(trend_df, x="Year", y=["Total_Admissions", "Readmitted_Relapse"], 
                       markers=True, title="PH Longitudinal Trend (2018-2024)")
        st.plotly_chart(fig1, use_container_width=True)
    with lc2:
        st.subheader("🏢 Socio-Economic Profile (2024)")
        fig2 = px.bar(demog_df, x="Category", y="Percentage", color="Category", title="Employment Status")
        st.plotly_chart(fig2, use_container_width=True)
    with lc3:
        st.subheader("💊 Primary Substances of Abuse")
        fig3 = px.pie(drug_df, names="Drug", values="Prevalence", hole=0.5, title="Main Drugs Reported")
        st.plotly_chart(fig3, use_container_width=True)

    # LOCAL Row 2
    lc4, lc5, lc6 = st.columns(3)
    with lc4:
        st.subheader("👥 Age Group Distribution")
        fig4 = px.bar(age_df, x="Age_Group", y=["Community_Rehab_Percent", "TRC_Rehab_Percent"],
                      barmode="group", title="Age Profile: Community vs. TRC")
        st.plotly_chart(fig4, use_container_width=True)
    with lc5:
        st.subheader("📍 Regional Admission (2024)")
        regions = pd.DataFrame({"Region": ["NCR", "Region III", "Region IV-A", "Others"], "Value": [26.6, 12.9, 11.2, 49.3]})
        fig5 = px.bar(regions, x="Value", y="Region", orientation='h', color="Region", title="Top Regional Admissions")
        st.plotly_chart(fig5, use_container_width=True)
    with lc6:
        st.subheader("🏥 Treatment Setting Ratio")
        labels = ['Residential', 'Outpatient']
        values = [latest['Total_Admissions'] - latest['Outpatient'], latest['Outpatient']]
        fig6 = px.pie(names=labels, values=values, title="Treatment Facility Type Split")
        st.plotly_chart(fig6, use_container_width=True)

# ------------------------------------------
# TAB 2: GLOBAL (BEHAVIORAL DATA) - 3x3 Layout
# ------------------------------------------
with tab2:
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("Sample Size", len(global_df))
    g2.metric("High Relapse Risk", len(global_df[global_df["Rehab_Outcome"] == "🚨 Relapse Risk"]))
    g3.metric("Avg Risk Severity", round(global_df["Severity"].mean(), 1))
    g4.metric("Academic Decline", f"{(global_df['Academic_Performance_Decline'] == 'Yes').mean()*100:.1f}%")

    st.divider()

    # GLOBAL Row 1
    gc1, gc2, gc3 = st.columns(3)
    with gc1:
        st.subheader("📊 Recovery Outcome Distribution")
        fig7 = px.pie(global_df, names="Rehab_Outcome", color="Rehab_Outcome", 
                      color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig7, use_container_width=True)
    with gc2:
        st.subheader("🧠 Denial & Resistance to Treatment")
        fig8 = px.histogram(global_df, x="Denial_and_Resistance_to_Treatment", color="Rehab_Outcome", barmode="group",
                            color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig8, use_container_width=True)
    with gc3:
        st.subheader("🏚️ Social Isolation & Relapse Risk")
        fig9 = px.bar(global_df, x="Social_Isolation", color="Rehab_Outcome", barmode="group",
                      color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig9, use_container_width=True)

    # GLOBAL Row 2
    gc4, gc5, gc6 = st.columns(3)
    with gc4:
        st.subheader("📉 Relationship Strain Frequency")
        fig10 = px.pie(global_df, names="Relationship_Strain", title="Impact on Social Relationships")
        st.plotly_chart(fig10, use_container_width=True)
    with gc5:
        st.subheader("💸 Financial Issues vs. Recovery")
        fig11 = px.histogram(global_df, x="Financial_Issues", color="Rehab_Outcome", barmode="group",
                             color_discrete_map={"✅ Successful Recovery": "#27AE60", "🚨 Relapse Risk": "#E74C3C"})
        st.plotly_chart(fig11, use_container_width=True)
    with gc6:
        st.subheader("⚖️ Legal Consequences Count")
        fig12 = px.bar(global_df, x="Legal_Consequences", color="Addiction_Class", title="Drug-Related Legal Incidents")
        st.plotly_chart(fig12, use_container_width=True)

    # GLOBAL Last Row (Full Width)
    st.divider()
    st.subheader("📈 Indicator Severity Trend")
    trend_data = global_df['Severity'].value_counts().sort_index().reset_index()
    trend_data.columns = ['Risk_Factors_Count', 'Student_Count']
    fig13 = px.line(trend_data, x="Risk_Factors_Count", y="Student_Count", markers=True, 
                    title="Volume of Cases by Cumulative Risk Factors")
    st.plotly_chart(fig13, use_container_width=True)

# ==========================================
# 5. DATA DICTIONARY & PROBLEM STATEMENT
# ==========================================
st.divider()
with st.expander("📖 View Data Dictionary & Documentation"):
    st.markdown("""
    ### Problem Statement
    To evaluate the success of addiction rehabilitation by monitoring national admission trends in the Philippines and identifying behavioral triggers (withdrawal, social isolation) that lead to relapse risk.

    ### Data Dictionary
    1. **Year:** (DDB) Annual reporting period from 2018-2024.
    2. **Readmitted_Relapse:** (DDB) Primary metric for treatment failure/relapse.
    3. **Rehab_Outcome:** (Global) Classification based on withdrawal and denial indicators.
    4. **Severity:** (Global) Sum of clinical indicators (Isolation, Finance, Legal, etc.).
    5. **Prevalence:** (DDB) Percentage of substances abused among the population.
    """)