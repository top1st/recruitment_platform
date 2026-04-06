import streamlit as st
import pandas as pd
from data import jobs, candidates
from analytics import HiringAnalytics
from matcher import auto_screen_candidates, rank_candidates_for_job, calculate_match_score

# Page configuration
st.set_page_config(
    page_title="AI Recruitment Platform",
    page_icon="🎯",
    layout="wide"
)

# Initialize analytics
analytics = HiringAnalytics(candidates, jobs)

# Title
st.title("🎯 AI-Powered Recruitment Platform")
st.markdown("*Automated CV Screening | Intelligent Matching | Real-time Analytics*")
st.markdown("---")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["📊 Hiring Dashboard", "🤖 AI Candidate Screening", "📝 Job Management", "📈 Detailed Analytics"]
)

# ==================== PAGE 1: HIRING DASHBOARD ====================
if page == "📊 Hiring Dashboard":
    st.header("📊 Hiring Dashboard - September 2021")
    
    # Get metrics
    internal = analytics.get_internal_metrics()
    external = analytics.get_external_metrics()
    referrals = analytics.get_referral_metrics()
    agency = analytics.get_agency_metrics()
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Internal Candidates",
            value=f"{internal['applications']} apps",
            delta=f"{internal['hires']} hires ({internal['conversion']}%)"
        )
    
    with col2:
        st.metric(
            label="External Candidates",
            value=f"{external['applications']} apps",
            delta=f"{external['hires']} hires ({external['conversion']}%)"
        )
    
    with col3:
        st.metric(
            label="Employee Referrals",
            value=f"{referrals['total_referrals']} total",
            delta=f"{referrals['successful']} hires ({referrals['conversion']}%)"
        )
    
    with col4:
        st.metric(
            label="Agency Placements",
            value=f"{agency['agencies']} agencies",
            delta=f"{agency['successful_placements']}/{agency['proposed_candidates']} placed ({agency['placement_rate']}%)"
        )
    
    st.markdown("---")
    
    # Distribution charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏢 Hires by Department")
        dept_data = analytics.get_hires_by_department()
        if dept_data:
            df_dept = pd.DataFrame(list(dept_data.items()), columns=["Department", "Percentage"])
            st.bar_chart(df_dept.set_index("Department"))
            st.dataframe(df_dept)
    
    with col2:
        st.subheader("💰 Hires by Paygrade")
        paygrade_data = analytics.get_hires_by_paygrade()
        if paygrade_data:
            df_paygrade = pd.DataFrame(list(paygrade_data.items()), columns=["Paygrade", "Percentage"])
            st.bar_chart(df_paygrade.set_index("Paygrade"))
            st.dataframe(df_paygrade)
    
    st.markdown("---")
    
    st.subheader("👥 Referrals by Department")
    referrals_by_dept = analytics.get_referrals_by_department()
    if referrals_by_dept:
        df_ref = pd.DataFrame(list(referrals_by_dept.items()), columns=["Department", "Number of Referrals"])
        st.dataframe(df_ref)

# ==================== PAGE 2: AI CANDIDATE SCREENING ====================
elif page == "🤖 AI Candidate Screening":
    st.header("🤖 AI-Powered Candidate Screening")
    
    # Select job
    job_options = {job["title"]: job_id for job_id, job in jobs.items()}
    selected_job_title = st.selectbox("Select Job to Screen For:", list(job_options.keys()))
    selected_job_id = job_options[selected_job_title]
    selected_job = jobs[selected_job_id]
    
    # Show job requirements
    with st.expander("📋 Job Requirements"):
        st.write(f"**Department:** {selected_job['dept']}")
        st.write(f"**Paygrade:** {selected_job['paygrade']}")
        st.write(f"**Required Skills:** {', '.join(selected_job['required_skills'])}")
    
    # Threshold slider
    threshold = st.slider(
        "Auto-screening threshold (%)",
        min_value=0,
        max_value=100,
        value=60,
        help="Candidates above this score are automatically shortlisted"
    )
    
    # Screen candidates
    if st.button("🚀 Run AI Screening", type="primary"):
        with st.spinner("Analyzing candidates..."):
            # Get candidates for this job
            job_candidates = [c for c in candidates if c.get("job_id") == selected_job_id]
            
            if not job_candidates:
                st.warning("No candidates found for this job.")
            else:
                # Auto-screen
                screened = auto_screen_candidates(job_candidates, selected_job, threshold)
                
                # Rank all
                ranked = rank_candidates_for_job(job_candidates, selected_job)
                
                st.success(f"✅ Screening complete! {len(screened)} candidates shortlisted out of {len(job_candidates)}")
                
                # Display results
                tab1, tab2 = st.tabs(["📋 Shortlisted Candidates", "📊 All Ranked Candidates"])
                
                with tab1:
                    if screened:
                        for idx, candidate in enumerate(screened, 1):
                            with st.container():
                                col1, col2, col3 = st.columns([2, 1, 1])
                                with col1:
                                    st.markdown(f"**{idx}. {candidate['name']}**")
                                with col2:
                                    st.markdown(f"Score: `{candidate['match_score']}%`")
                                with col3:
                                    if candidate['status'] == 'hired':
                                        st.markdown("✅ **Hired**")
                                    else:
                                        st.button(f"Contact {candidate['name']}", key=f"contact_{candidate['id']}")
                                
                                st.markdown(f"*{candidate['match_reason']}*")
                                if candidate.get('missing_skills'):
                                    st.markdown(f"⚠️ Missing skills: {', '.join(candidate['missing_skills'])}")
                                st.markdown("---")
                    else:
                        st.info("No candidates passed the screening threshold.")
                
                with tab2:
                    ranked_data = []
                    for candidate in ranked:
                        ranked_data.append({
                            "Name": candidate['name'],
                            "Source": candidate['source'].upper(),
                            "Experience (years)": candidate['exp'],
                            "Match Score": f"{candidate['match_score']}%",
                            "Status": candidate['status'].upper(),
                            "Recommendation": candidate['match_reason']
                        })
                    
                    df_ranked = pd.DataFrame(ranked_data)
                    st.dataframe(df_ranked, use_container_width=True)

# ==================== PAGE 3: JOB MANAGEMENT ====================
elif page == "📝 Job Management":
    st.header("📝 Job Management")
    
    # Display existing jobs
    st.subheader("Current Open Positions")
    job_data = []
    for job_id, job in jobs.items():
        candidate_count = len([c for c in candidates if c.get("job_id") == job_id])
        hired_count = len([c for c in candidates if c.get("job_id") == job_id and c.get("status") == "hired"])
        
        job_data.append({
            "Job ID": job_id,
            "Title": job['title'],
            "Department": job['dept'],
            "Paygrade": job['paygrade'],
            "Candidates": candidate_count,
            "Hired": hired_count
        })
    
    df_jobs = pd.DataFrame(job_data)
    st.dataframe(df_jobs, use_container_width=True)
    
    # Add new job form
    with st.expander("➕ Add New Job Position"):
        with st.form("new_job_form"):
            new_title = st.text_input("Job Title")
            new_dept = st.selectbox("Department", ["Engineering", "HR", "Finance", "Programs", "Operations", "Marketing", "Sales"])
            new_paygrade = st.selectbox("Paygrade", ["GR-6", "GR-7", "GR-8", "GR-9", "GR-10"])
            new_skills = st.text_input("Required Skills (comma-separated)", placeholder="e.g., python, sql, communication")
            
            submitted = st.form_submit_button("Create Job")
            
            if submitted and new_title:
                new_id = max(jobs.keys()) + 1
                jobs[new_id] = {
                    "id": new_id,
                    "title": new_title,
                    "dept": new_dept,
                    "paygrade": new_paygrade,
                    "required_skills": [s.strip().lower() for s in new_skills.split(",")]
                }
                st.success(f"✅ Job '{new_title}' created successfully!")
                st.rerun()

# ==================== PAGE 4: DETAILED ANALYTICS ====================
else:
    st.header("📈 Detailed Hiring Analytics")
    
    # Source breakdown
    st.subheader("Candidate Source Breakdown")
    source_counts = {
        "Internal": len([c for c in candidates if c['source'] == 'internal']),
        "External": len([c for c in candidates if c['source'] == 'external']),
        "Referral": len([c for c in candidates if c['source'] == 'referral']),
        "Agency": len([c for c in candidates if c['source'] == 'agency'])
    }
    
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(source_counts)
    with col2:
        df_source = pd.DataFrame(list(source_counts.items()), columns=["Source", "Count"])
        st.dataframe(df_source)
    
    # Conversion funnel
    st.subheader("🎯 Conversion Funnel by Source")
    funnel_data = []
    for source in ['internal', 'external', 'referral', 'agency']:
        source_candidates = [c for c in candidates if c['source'] == source]
        total = len(source_candidates)
        screened = len([c for c in source_candidates if c['status'] in ['screened', 'hired']])
        hired = len([c for c in source_candidates if c['status'] == 'hired'])
        
        funnel_data.append({
            "Source": source.upper(),
            "Total Applications": total,
            "Screened": screened,
            "Hired": hired,
            "Conversion Rate": f"{(hired/total*100):.1f}%" if total > 0 else "0%"
        })
    
    df_funnel = pd.DataFrame(funnel_data)
    st.dataframe(df_funnel, use_container_width=True)
    
    # Candidate list
    st.subheader("📋 All Candidates")
    df_all = pd.DataFrame(candidates)
    df_all['match_score'] = df_all.apply(lambda row: calculate_match_score(row, jobs.get(row.get('job_id', 1), {}))['score'], axis=1)
    st.dataframe(df_all[['name', 'source', 'exp', 'status', 'match_score']], use_container_width=True)
    
    # Export option
    if st.button("📥 Export Report (CSV)"):
        csv = df_all.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="recruitment_report.csv",
            mime="text/csv"
        )

st.markdown("---")
st.caption("🎯 AI-Powered Recruitment Platform | Automated Screening & Analytics")