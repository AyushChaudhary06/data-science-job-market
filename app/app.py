"""
app/app.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
India Job Market Intelligence Dashboard
Streamlit App — reads from data/processed/cleaned_jobs.csv

Run:
  streamlit run app/app.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import re
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="India Job Market Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data" / "processed"
CLEANED    = DATA_DIR / "cleaned_jobs.csv"
SKILLS_CSV = DATA_DIR / "skills_data.csv"


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data
def load_data():
    df = pd.read_csv(CLEANED, low_memory=False)

    # Clean sentinel values
    df.replace(-1, pd.NA, inplace=True)
    df.replace("-1", pd.NA, inplace=True)

    # Parse salary
    def parse_salary(s):
        if pd.isna(s):
            return None
        nums = re.findall(r"\$?(\d+)K?", str(s).replace(",", ""))
        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2
        if len(nums) == 1:
            return float(nums[0])
        return None

    df["salary_mid"] = df["Salary Estimate"].apply(parse_salary)

    # Normalize job title
    def norm_title(t):
        if pd.isna(t):
            return "Other"
        t = str(t).lower()
        if "machine learning" in t or "ml engineer" in t:
            return "ML Engineer"
        if "data engineer" in t:
            return "Data Engineer"
        if "data scientist" in t:
            return "Data Scientist"
        if "business analyst" in t or "business intelligence" in t:
            return "Business Analyst"
        if "data analyst" in t or "analytics" in t:
            return "Data Analyst"
        if "bi developer" in t or "bi analyst" in t:
            return "BI Developer"
        return "Other"

    df["role"] = df["Job Title"].apply(norm_title)

    # Parse city
    def parse_city(loc):
        if pd.isna(loc):
            return None
        return str(loc).split(",")[0].strip()

    df["city"] = df["Location"].apply(parse_city)

    # Rating to numeric
    df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
    df.loc[df["Rating"] <= 0, "Rating"] = pd.NA

    # Company name clean
    df["company_clean"] = df["Company Name"].astype(str).str.replace(r"\n.*", "", regex=True).str.strip()

    return df


@st.cache_data
def load_skills():
    df = pd.read_csv(SKILLS_CSV, low_memory=False)
    df.replace(-1, pd.NA, inplace=True)
    df.replace("-1", pd.NA, inplace=True)

    # Find skill column
    skill_col = None
    for col in df.columns:
        if col.lower() in ("skill", "skills", "skill_name"):
            skill_col = col
            break

    if skill_col:
        df = df.rename(columns={skill_col: "skill"})
    else:
        # Skills are comma-separated in 'Skills' column — explode them
        df["skill"] = df["Skills"].astype(str).str.split(",")
        df = df.explode("skill")
        df["skill"] = df["skill"].str.strip()

    def norm_title(t):
        if pd.isna(t):
            return "Other"
        t = str(t).lower()
        if "machine learning" in t or "ml engineer" in t:
            return "ML Engineer"
        if "data engineer" in t:
            return "Data Engineer"
        if "data scientist" in t:
            return "Data Scientist"
        if "business analyst" in t or "business intelligence" in t:
            return "Business Analyst"
        if "data analyst" in t or "analytics" in t:
            return "Data Analyst"
        if "bi developer" in t or "bi analyst" in t:
            return "BI Developer"
        return "Other"

    df["role"] = df["Job Title"].apply(norm_title)
    df["city"] = df["Location"].astype(str).str.split(",").str[0].str.strip()

    def parse_salary(s):
        if pd.isna(s):
            return None
        nums = re.findall(r"\$?(\d+)K?", str(s).replace(",", ""))
        if len(nums) >= 2:
            return (float(nums[0]) + float(nums[1])) / 2
        return None

    df["salary_mid"] = df["Salary Estimate"].apply(parse_salary)
    df = df[df["skill"].notna() & (df["skill"] != "") & (df["skill"] != "nan")]
    return df


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

def sidebar(df):
    st.sidebar.image("https://img.icons8.com/fluency/96/analytics.png", width=60)
    st.sidebar.title("Job Market Intel")
    st.sidebar.markdown("---")

    page = st.sidebar.radio(
        "Navigate",
        ["📊 Market Snapshot", "🔧 Skill Demand", "💰 Salary Analysis", "🏢 Company Intel"],
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Filters")

    roles = ["All"] + sorted(df["role"].dropna().unique().tolist())
    sel_role = st.sidebar.selectbox("Role", roles)

    cities = ["All"] + sorted(df["city"].dropna().value_counts().head(20).index.tolist())
    sel_city = st.sidebar.selectbox("City", cities)

    sectors = ["All"] + sorted(df["Sector"].dropna().unique().tolist())
    sel_sector = st.sidebar.selectbox("Sector", sectors)

    st.sidebar.markdown("---")
    st.sidebar.caption("Data: Glassdoor DA/DS Jobs")
    st.sidebar.caption(f"Total records: {len(df):,}")

    return page, sel_role, sel_city, sel_sector


def apply_filters(df, role, city, sector):
    if role != "All":
        df = df[df["role"] == role]
    if city != "All":
        df = df[df["city"] == city]
    if sector != "All":
        df = df[df["Sector"] == sector]
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: MARKET SNAPSHOT
# ══════════════════════════════════════════════════════════════════════════════

def page_snapshot(df):
    st.title("📊 Market Snapshot")
    st.markdown("High-level overview of the DA/DS job market.")

    # KPI tiles
    col1, col2, col3, col4, col5 = st.columns(5)
    with_sal = df[df["salary_mid"].notna()]

    col1.metric("Total Job Postings",  f"{len(df):,}")
    col2.metric("Unique Companies",    f"{df['company_clean'].nunique():,}")
    col3.metric("Cities Covered",      f"{df['city'].nunique():,}")
    col4.metric("Avg Salary",
                f"${with_sal['salary_mid'].mean():.0f}K" if len(with_sal) else "N/A")
    col5.metric("Avg Company Rating",
                f"{df['Rating'].mean():.2f} ⭐" if df['Rating'].notna().any() else "N/A")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Jobs by Role")
        role_counts = df["role"].value_counts().reset_index()
        role_counts.columns = ["Role", "Count"]
        fig = px.bar(role_counts, x="Count", y="Role", orientation="h",
                     color="Count", color_continuous_scale="Blues",
                     text="Count")
        fig.update_layout(showlegend=False, height=350,
                          margin=dict(l=0, r=0, t=10, b=0),
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Jobs by Sector")
        sector_counts = df["Sector"].value_counts().head(10).reset_index()
        sector_counts.columns = ["Sector", "Count"]
        fig = px.pie(sector_counts, names="Sector", values="Count",
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(height=350, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Top 15 Hiring Cities")
        city_counts = df["city"].value_counts().head(15).reset_index()
        city_counts.columns = ["City", "Count"]
        fig = px.bar(city_counts, x="City", y="Count",
                     color="Count", color_continuous_scale="Teal",
                     text="Count")
        fig.update_layout(showlegend=False, height=350,
                          margin=dict(l=0, r=0, t=10, b=0))
        fig.update_traces(textposition="outside")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Company Size Distribution")
        size_order = [
            "1 to 50 Employees", "51 to 200 Employees", "201 to 500 Employees",
            "501 to 1000 Employees", "1001 to 5000 Employees",
            "5001 to 10000 Employees", "10000+ Employees",
        ]
        size_counts = df["Size"].value_counts().reset_index()
        size_counts.columns = ["Size", "Count"]
        size_counts = size_counts[size_counts["Size"].isin(size_order)]
        size_counts["Size"] = pd.Categorical(size_counts["Size"],
                                              categories=size_order, ordered=True)
        size_counts = size_counts.sort_values("Size")
        fig = px.bar(size_counts, x="Size", y="Count",
                     color="Count", color_continuous_scale="Purples",
                     text="Count")
        fig.update_layout(showlegend=False, height=350,
                          margin=dict(l=0, r=0, t=10, b=0))
        fig.update_traces(textposition="outside")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: SKILL DEMAND
# ══════════════════════════════════════════════════════════════════════════════

def page_skills(df_jobs, skills_df, sel_role, sel_city):
    st.title("🔧 Skill Demand Analysis")

    # Filter skills
    s = skills_df.copy()
    if sel_role != "All":
        s = s[s["role"] == sel_role]
    if sel_city != "All":
        s = s[s["city"] == sel_city]

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 20 Most Demanded Skills")
        top_skills = s["skill"].value_counts().head(20).reset_index()
        top_skills.columns = ["Skill", "Count"]
        fig = px.bar(top_skills, x="Count", y="Skill", orientation="h",
                     color="Count", color_continuous_scale="Oranges", text="Count")
        fig.update_layout(showlegend=False, height=500,
                          margin=dict(l=0, r=0, t=10, b=0),
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Skills by Role — Heatmap")
        pivot = (
            s.groupby(["role", "skill"])
            .size()
            .reset_index(name="count")
        )
        top_sk = s["skill"].value_counts().head(15).index.tolist()
        pivot  = pivot[pivot["skill"].isin(top_sk)]
        pivot_wide = pivot.pivot(index="role", columns="skill", values="count").fillna(0)
        fig = px.imshow(
            pivot_wide,
            color_continuous_scale="Blues",
            aspect="auto",
            text_auto=True,
        )
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Skill gap analyzer
    st.markdown("---")
    st.subheader("🎯 Skill Gap Analyzer")
    st.markdown("Select a target role and see which skills you need most.")

    target = st.selectbox("Target Role", sorted(s["role"].dropna().unique()))
    role_skills = s[s["role"] == target]["skill"].value_counts().head(15)

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(
            role_skills.reset_index().rename(columns={"index": "Skill", "skill": "Count",
                                                       "count": "Count"}),
            x=role_skills.values, y=role_skills.index,
            orientation="h",
            labels={"x": "Job Count", "y": "Skill"},
            color=role_skills.values,
            color_continuous_scale="Teal",
            text=role_skills.values,
        )
        fig.update_layout(showlegend=False, height=400,
                          margin=dict(l=0, r=0, t=10, b=0),
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        total = len(s[s["role"] == target]["skill"].index)
        st.markdown(f"**Top skills for {target}:**")
        for skill, count in role_skills.items():
            pct = int(100 * count / max(len(s[s["role"] == target]), 1))
            st.markdown(f"- **{skill}** — {pct}% of postings")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: SALARY ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════

def page_salary(df):
    st.title("💰 Salary Analysis")

    df_sal = df[df["salary_mid"].notna()].copy()

    if len(df_sal) == 0:
        st.warning("No salary data available with current filters.")
        return

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Salary by Role")
        fig = px.box(df_sal, x="role", y="salary_mid",
                     color="role",
                     labels={"salary_mid": "Salary ($K)", "role": "Role"},
                     color_discrete_sequence=px.colors.qualitative.Set2)
        fig.update_layout(showlegend=False, height=400,
                          margin=dict(l=0, r=0, t=10, b=0))
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Salary by Sector (Top 10)")
        sector_sal = (
            df_sal.groupby("Sector")["salary_mid"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "Avg Salary", "count": "Jobs"})
            .query("Jobs >= 5")
            .sort_values("Avg Salary", ascending=False)
            .head(10)
        )
        fig = px.bar(sector_sal, x="Avg Salary", y="Sector", orientation="h",
                     color="Avg Salary", color_continuous_scale="Greens",
                     text=sector_sal["Avg Salary"].round(1))
        fig.update_layout(showlegend=False, height=400,
                          margin=dict(l=0, r=0, t=10, b=0),
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_traces(textposition="outside",
                          texttemplate="%{text}K")
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Salary by Company Size")
        size_order = [
            "1 to 50 Employees", "51 to 200 Employees",
            "201 to 500 Employees", "501 to 1000 Employees",
            "1001 to 5000 Employees", "5001 to 10000 Employees",
            "10000+ Employees",
        ]
        size_sal = (
            df_sal[df_sal["Size"].isin(size_order)]
            .groupby("Size")["salary_mid"]
            .mean()
            .reindex([s for s in size_order if s in df_sal["Size"].values])
            .reset_index()
            .rename(columns={"salary_mid": "Avg Salary"})
        )
        fig = px.bar(size_sal, x="Size", y="Avg Salary",
                     color="Avg Salary", color_continuous_scale="Purples",
                     text=size_sal["Avg Salary"].round(1))
        fig.update_layout(showlegend=False, height=380,
                          margin=dict(l=0, r=0, t=10, b=0))
        fig.update_traces(textposition="outside", texttemplate="%{text}K")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    with col_d:
        st.subheader("Top Paying Cities")
        city_sal = (
            df_sal.groupby("city")["salary_mid"]
            .agg(["mean", "count"])
            .reset_index()
            .rename(columns={"mean": "Avg Salary", "count": "Jobs"})
            .query("Jobs >= 5")
            .sort_values("Avg Salary", ascending=False)
            .head(12)
        )
        fig = px.bar(city_sal, x="city", y="Avg Salary",
                     color="Avg Salary", color_continuous_scale="Oranges",
                     text=city_sal["Avg Salary"].round(1))
        fig.update_layout(showlegend=False, height=380,
                          margin=dict(l=0, r=0, t=10, b=0))
        fig.update_traces(textposition="outside", texttemplate="%{text}K")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # Rating vs Salary scatter
    st.markdown("---")
    st.subheader("Company Rating vs Salary")
    df_scatter = df_sal[df_sal["Rating"].notna()].copy()
    fig = px.scatter(
        df_scatter, x="Rating", y="salary_mid",
        color="role", size_max=10,
        hover_data=["company_clean", "city"],
        labels={"salary_mid": "Salary ($K)", "Rating": "Company Rating"},
        opacity=0.7,
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: COMPANY INTEL
# ══════════════════════════════════════════════════════════════════════════════

def page_companies(df):
    st.title("🏢 Company Intelligence")

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Top 20 Hiring Companies")
        top_cos = (
            df.groupby("company_clean")
            .agg(
                Jobs=("Job Title", "count"),
                Avg_Salary=("salary_mid", "mean"),
                Rating=("Rating", "mean"),
            )
            .reset_index()
            .sort_values("Jobs", ascending=False)
            .head(20)
        )
        top_cos["Avg_Salary"] = top_cos["Avg_Salary"].round(1)
        top_cos["Rating"]     = top_cos["Rating"].round(2)
        fig = px.bar(top_cos, x="Jobs", y="company_clean", orientation="h",
                     color="Avg_Salary", color_continuous_scale="Blues",
                     text="Jobs",
                     labels={"company_clean": "Company"})
        fig.update_layout(showlegend=False, height=550,
                          margin=dict(l=0, r=0, t=10, b=0),
                          yaxis=dict(categoryorder="total ascending"))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Ownership Type — Jobs & Salary")
        own_data = (
            df.groupby("Type of ownership")
            .agg(Jobs=("Job Title", "count"),
                 Avg_Salary=("salary_mid", "mean"))
            .reset_index()
            .dropna(subset=["Type of ownership"])
            .query("`Type of ownership` not in ['-1', 'Unknown']")
            .sort_values("Jobs", ascending=False)
            .head(8)
        )
        fig = px.bar(own_data, x="Type of ownership", y="Jobs",
                     color="Avg_Salary", color_continuous_scale="Teal",
                     text="Jobs")
        fig.update_layout(showlegend=False, height=350,
                          margin=dict(l=0, r=0, t=10, b=0))
        fig.update_traces(textposition="outside")
        fig.update_xaxes(tickangle=30)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Company Age vs Hiring")
        df_age = df[df["Founded"].notna() & (df["Founded"] > 0)].copy()
        df_age["Founded"] = pd.to_numeric(df_age["Founded"], errors="coerce")
        df_age = df_age.dropna(subset=["Founded"])
        df_age["Age Bucket"] = pd.cut(
            df_age["Founded"],
            bins=[0, 1990, 2005, 2015, 2025],
            labels=["Legacy (pre-1990)", "Established (1990-2004)",
                    "Mid (2005-2014)", "New (2015+)"],
        )
        age_counts = df_age["Age Bucket"].value_counts().reset_index()
        age_counts.columns = ["Age Bucket", "Count"]
        fig = px.pie(age_counts, names="Age Bucket", values="Count",
                     hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_layout(height=280, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Detailed company table
    st.markdown("---")
    st.subheader("🔍 Company Explorer")
    search = st.text_input("Search company name", "")
    company_table = (
        df.groupby("company_clean")
        .agg(
            Sector=("Sector", "first"),
            Industry=("Industry", "first"),
            Size=("Size", "first"),
            Jobs=("Job Title", "count"),
            Avg_Salary_K=("salary_mid", lambda x: round(x.mean(), 1)
                          if x.notna().any() else None),
            Rating=("Rating", lambda x: round(x.mean(), 2)
                    if x.notna().any() else None),
            Cities=("city", lambda x: ", ".join(sorted(x.dropna().unique()[:3]))),
        )
        .reset_index()
        .rename(columns={"company_clean": "Company"})
        .sort_values("Jobs", ascending=False)
    )
    if search:
        company_table = company_table[
            company_table["Company"].str.lower().str.contains(search.lower(), na=False)
        ]
    st.dataframe(company_table, use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    df        = load_data()
    skills_df = load_skills()

    page, sel_role, sel_city, sel_sector = sidebar(df)
    df_filtered = apply_filters(df, sel_role, sel_city, sel_sector)

    if page == "📊 Market Snapshot":
        page_snapshot(df_filtered)
    elif page == "🔧 Skill Demand":
        page_skills(df_filtered, skills_df, sel_role, sel_city)
    elif page == "💰 Salary Analysis":
        page_salary(df_filtered)
    elif page == "🏢 Company Intel":
        page_companies(df_filtered)


if __name__ == "__main__":
    main()
