import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set page layout configuration
st.set_page_config(
    page_title="Marketing Analytics Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Data Loading Engine (Cached)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data(file_path="marketing_updated.csv"):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Could not locate '{file_path}' in your current workspace directory.")
    
    # Read file using utf-8-sig to clear hidden BOM artifacts from Excel
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    # Standardize column headers to lowercase to avoid indexing errors
    df.columns = df.columns.str.strip().str.lower()
    return df

try:
    df = load_data("marketing_updated.csv")
except Exception as e:
    st.error(f"❌ Error loading dataset: {e}")
    st.info("💡 Ensure 'marketing_updated.csv' is placed inside this exact project workspace directory.")
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar Navigation Hub & Global Interactivity Controls
# -----------------------------------------------------------------------------
st.sidebar.title("App Navigation")
app_page = st.sidebar.radio(
    "Go To Page:",
    [
        "Page 1: Demographics Distribution",
        "Page 2: Product Expenditures",
        "Page 3: Engagement & Campaigns",
        "Page 4: Creator Info"
    ]
)

# Shared Interactive Radio Filters for Page 2 and Page 3
selected_age_filter = "All"
selected_inc_filter = "All"

if app_page in ["Page 2: Product Expenditures", "Page 3: Engagement & Campaigns"]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Live Dashboard Sub-segmentation Filters")
    
    # Age Group Radio Configuration
    if 'age_group' in df.columns:
        age_options = ["All"] + sorted(list(df['age_group'].dropna().unique()))
        selected_age_filter = st.sidebar.radio("Select Target Age Group:", age_options, key="global_age_radio")
    
    # Income Group Radio Configuration
    if 'income_group' in df.columns:
        inc_options = ["All"] + sorted(list(df['income_group'].dropna().unique()))
        selected_inc_filter = st.sidebar.radio("Select Target Income Group:", inc_options, key="global_inc_radio")

# -----------------------------------------------------------------------------
# PAGE 1: DEMOGRAPHICS DISTRIBUTION
# -----------------------------------------------------------------------------
if app_page == "Page 1: Demographics Distribution":
    st.title("👥 Page 1: Customer Demographics Profile Distribution")
    st.markdown("Analyze baseline cohort volumes and isolate target profile attributes.")
    
    # Visual Chart Breakdowns Row
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.subheader("Age Group Distribution")
        if 'age_group' in df.columns:
            age_counts = df['age_group'].value_counts().reset_index()
            age_counts.columns = ['Age Group', 'Headcount']
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.barplot(data=age_counts, x='Age Group', y='Headcount', palette="Blues_d", ax=ax)
            plt.xticks(rotation=15)
            st.pyplot(fig)
        else:
            st.warning("'age_group' column missing.")

    with c2:
        st.subheader("Income Group Distribution")
        if 'income_group' in df.columns:
            inc_counts = df['income_group'].value_counts().reset_index()
            inc_counts.columns = ['Income Group', 'Headcount']
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.barplot(data=inc_counts, x='Income Group', y='Headcount', palette="Greens_d", ax=ax)
            plt.xticks(rotation=15)
            st.pyplot(fig)
        else:
            st.warning("'income_group' column missing.")

    with c3:
        st.subheader("Children Distribution")
        if 'children' in df.columns:
            child_counts = df['children'].value_counts().reset_index()
            child_counts.columns = ['Children Count', 'Headcount']
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.barplot(data=child_counts, x='Children Count', y='Headcount', palette="Purples_d", ax=ax)
            st.pyplot(fig)
        elif 'kids' in df.columns:
            # Fallback if the dataset splits it under 'kids'
            kid_counts = df['kids'].value_counts().reset_index()
            kid_counts.columns = ['Kids Count', 'Headcount']
            fig, ax = plt.subplots(figsize=(5, 4))
            sns.barplot(data=kid_counts, x='Kids Count', y='Headcount', palette="Purples_d", ax=ax)
            st.pyplot(fig)
        else:
            st.warning("'children' column missing.")

    st.markdown("---")
    st.subheader("🔍 Dynamic Profile Expansion Section")
    
    f1, f2, f3 = st.columns(3)
    with f1:
        p1_age_opts = ["All"] + sorted(list(df['age_group'].dropna().unique())) if 'age_group' in df.columns else ["All"]
        sel_age = st.selectbox("Filter Data Table by Age Group:", p1_age_opts)
    with f2:
        p1_inc_opts = ["All"] + sorted(list(df['income_group'].dropna().unique())) if 'income_group' in df.columns else ["All"]
        sel_inc = st.selectbox("Filter Data Table by Income Group:", p1_inc_opts)
    with f3:
        child_col_name = 'children' if 'children' in df.columns else ('kids' if 'kids' in df.columns else None)
        if child_col_name:
            p1_child_opts = ["All"] + sorted([str(int(x)) for x in df[child_col_name].dropna().unique()])
            sel_child = st.selectbox("Filter Data Table by Children Count:", p1_child_opts)
        else:
            sel_child = "All"

    # Apply Filters to Table Expansion
    filt_df = df.copy()
    if sel_age != "All":
        filt_df = filt_df[filt_df['age_group'] == sel_age]
    if sel_inc != "All":
        filt_df = filt_df[filt_df['income_group'] == sel_inc]
    if sel_child != "All" and child_col_name:
        filt_df = filt_df[filt_df[child_col_name] == int(sel_child)]

    with st.expander(f"📋 Expand Customer Base Logbook ({len(filt_df)} matching lines found)", expanded=True):
        st.dataframe(filt_df, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 2: PRODUCT EXPENDITURES (FILTERED VIA SIDEBAR RADIOS)
# -----------------------------------------------------------------------------
elif app_page == "Page 2: Product Expenditures":
    st.title("🛍️ Page 2: Product Spending Profiles & Total Wallet Analysis")
    st.markdown(f"**Current Segment Focus:** Age Group = `{selected_age_filter}` | Income Group = `{selected_inc_filter}`")

    # Apply Sidebar Radio Filter Selections to Dataset
    p2_df = df.copy()
    if selected_age_filter != "All":
        p2_df = p2_df[p2_df['age_group'] == selected_age_filter]
    if selected_inc_filter != "All":
        p2_df = p2_df[p2_df['income_group'] == selected_inc_filter]

    spend_cols = ['wine_spend', 'fruits_spend', 'meat_spend', 'fish_spend', 'sweets_spend', 'gold_spend']
    valid_spends = [c for c in spend_cols if c in p2_df.columns]

    if len(p2_df) == 0:
        st.warning("⚠️ No customer records match the cross-selected segment criteria in the sidebar.")
    elif valid_spends:
        # Segment KPI Summaries
        total_revenue = p2_df['total_spend'].sum() if 'total_spend' in p2_df.columns else p2_df[valid_spends].sum().sum()
        avg_spend = p2_df['total_spend'].mean() if 'total_spend' in p2_df.columns else p2_df[valid_spends].sum(axis=1).mean()

        m1, m2, m3 = st.columns(3)
        m1.metric("Segment Record Headcount", f"{len(p2_df):,}")
        m2.metric("Segment Total Spend", f"${total_revenue:,.2f}")
        m3.metric("Segment Avg Household Spend", f"${avg_spend:,.2f}")

        st.markdown("---")
        
        # Segment product wise average distribution chart
        st.subheader("📦 Mean Product Expenditure Categories Breakdown (Filtered Segment)")
        fig, ax = plt.subplots(figsize=(10, 3.5))
        mean_vals = p2_df[valid_spends].mean().sort_values(ascending=False)
        sns.barplot(x=mean_vals.values, y=[c.replace('_',' ').title() for c in mean_vals.index], palette="rocket", ax=ax)
        ax.set_xlabel("Mean Ticket Value ($)")
        st.pyplot(fig)

        # Segment level granular data matrix view
        st.markdown("---")
        st.subheader("📋 Segment Transactional Spend Logbook")
        view_cols = ['id'] + valid_spends + (['total_spend'] if 'total_spend' in p2_df.columns else [])
        st.dataframe(p2_df[[c for c in view_cols if c in p2_df.columns]], use_container_width=True)
    else:
        st.error("No valid spend data metric vectors found in data headers structure.")

# -----------------------------------------------------------------------------
# PAGE 3: ENGAGEMENT & CAMPAIGNS (FILTERED VIA SIDEBAR RADIOS)
# -----------------------------------------------------------------------------
elif app_page == "Page 3: Engagement & Campaigns":
    st.title("🎯 Page 3: Conversion Flags, Campaigns & Retention Insights")
    st.markdown(f"**Current Segment Focus:** Age Group = `{selected_age_filter}` | Income Group = `{selected_inc_filter}`")

    # Apply Sidebar Radio Filter Selections to Dataset
    p3_df = df.copy()
    if selected_age_filter != "All":
        p3_df = p3_df[p3_df['age_group'] == selected_age_filter]
    if selected_inc_filter != "All":
        p3_df = p3_df[p3_df['income_group'] == selected_inc_filter]

    if len(p3_df) == 0:
        st.warning("⚠️ No customer records match the cross-selected segment criteria in the sidebar.")
    else:
        # Segment behavioral highlights
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Segment Record Headcount", f"{len(p3_df):,}")
        k2.metric("Segment Avg Monthly Web Visits", f"{p3_df['web_monthly_visit'].mean():.2f}" if 'web_monthly_visit' in p3_df.columns else "N/A")
        k3.metric("Segment Avg Total Spend", f"${p3_df['total_spend'].mean():,.2f}" if 'total_spend' in p3_df.columns else "N/A")
        k4.metric("Segment Avg Campaign Response Rate", f"{p3_df['response'].mean() * 100:.2f}%" if 'response' in p3_df.columns else "N/A")

        st.markdown("---")# Campaign Performance Segment Split
        st.subheader("📢 Campaign Performance & Opt-in Tracking (Filtered Segment)")
        cmp_cols = ['acceptedcmp1', 'acceptedcmp2', 'acceptedcmp3', 'acceptedcmp4',
                     'acceptedcmp5', 'response']
        valid_cmps = [c for c in cmp_cols if c in p3_df.columns]
        if valid_cmps:
            cmp_totals = p3_df[valid_cmps].sum().to_frame(name="Total Opt-ins")
            cmp_totals["Conversion Rate (%)"] = (cmp_totals["Total Opt-ins"] / len(p3_df)) * 100
            cmp_totals.index = [c.replace('acceptedcmp', 'Campaign ').title() for c in cmp_totals.index]
            c_left, c_right = st.columns([1, 1.5])
            with c_left:
                st.dataframe(cmp_totals.style.format({"Conversion Rate (%)": "{:.2f}%"}))
            with c_right:
                fig, ax = plt.subplots(figsize=(6, 3.2))
                sns.barplot(x=cmp_totals["Conversion Rate (%)"].values, y=cmp_totals.index, palette="viridis", ax=ax)
                ax.set_xlabel("Conversion Rate (%)")
                st.pyplot(fig)
        else:
            st.warning("No campaign column metrics discovered in layout.")
        st.markdown("---")
        st.subheader("📋 Segment Engagement Matrix Data")
        behavioral_cols = ['id', 'recency', 'complain', 'web_monthly_visit'] + valid_cmps
        st.dataframe(p3_df[[c for c in behavioral_cols if c in p3_df.columns]], use_container_width=True)

#----------------------------------------------------------------------------PAGE 4: CREATOR INFO-----------------------------------------------------------------------------
elif app_page == "Page 4: Creator Info":
        st.title("🛠️ Page 4: Architecture Creator Pipeline Profile")
        with st.container(border=True):
             st.subheader("🎓 Professional Structural Profile")
        col_img, col_txt = st.columns([1, 5])
        with col_img:
            st.markdown("## 👨‍💻")
        with col_txt:
            st.markdown("### Sidharath Singh")
            st.write("✨ Domain Specialization: Data Science Engineering")
            st.write("📚 Academic Suite: Data Science Course Pipeline Project Portfolio")
        st.markdown("---")
        st.subheader("⚙️ Technical System Architecture Metadata")
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.info("💻 Front-End Layout Interface: Multi-page Streamlit Dashboard Module Layout Configuration with dynamic global side-filters.")
            st.success("📦 Backend Cache Configuration: Performance @st.cache_data safely optimization handling rapid UI rendering calculations.")
        with info_col2:
            st.metric("Total Managed Columns Feature Metrics Count", f"{len(df.columns)}")
            st.metric("Total Scaled Relational File Records", f"{len(df):,}")                 
