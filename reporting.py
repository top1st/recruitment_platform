import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import streamlit as st
from datetime import datetime

class RecruitmentReporter:
    def __init__(self, candidates: list, jobs: dict, analytics):
        self.candidates = candidates
        self.jobs = jobs
        self.analytics = analytics
    
    def create_advanced_charts(self):
        """Create interactive Plotly charts"""
        
        # 1. Conversion funnel chart
        sources = ['Internal', 'External', 'Referral', 'Agency']
        applications = []
        hires = []
        
        for source in ['internal', 'external', 'referral', 'agency']:
            source_candidates = [c for c in self.candidates if c['source'] == source]
            applications.append(len(source_candidates))
            hires.append(len([c for c in source_candidates if c['status'] == 'hired']))
        
        fig_funnel = make_subplots(rows=1, cols=2, 
                                   subplot_titles=('Applications by Source', 'Hires by Source'))
        
        fig_funnel.add_trace(go.Bar(x=sources, y=applications, name='Applications', 
                                    marker_color='lightblue'), row=1, col=1)
        fig_funnel.add_trace(go.Bar(x=sources, y=hires, name='Hires', 
                                    marker_color='darkgreen'), row=1, col=2)
        
        fig_funnel.update_layout(height=400, showlegend=True, 
                                 title_text="Recruitment Funnel Analysis")
        
        # 2. Department distribution pie chart
        dept_data = self.analytics.get_hires_by_department()
        if dept_data:
            fig_dept = go.Figure(data=[go.Pie(labels=list(dept_data.keys()), 
                                             values=list(dept_data.values()),
                                             hole=.3)])
            fig_dept.update_layout(title="Hires by Department", height=400)
        else:
            fig_dept = None
        
        # 3. Match score distribution
        match_scores = []
        for candidate in self.candidates:
            job = self.jobs.get(candidate.get('job_id', 1))
            if job:
                from matcher import calculate_match_score
                score = calculate_match_score(candidate, job)['score']
                match_scores.append(score)
        
        fig_scores = go.Figure(data=[go.Histogram(x=match_scores, nbinsx=20, 
                                                  marker_color='coral')])
        fig_scores.update_layout(title="Candidate Match Score Distribution",
                                 xaxis_title="Match Score (%)",
                                 yaxis_title="Number of Candidates",
                                 height=400)
        
        # 4. Source effectiveness heatmap
        source_success = []
        for source in ['internal', 'external', 'referral', 'agency']:
            source_candidates = [c for c in self.candidates if c['source'] == source]
            total = len(source_candidates)
            hired = len([c for c in source_candidates if c['status'] == 'hired'])
            conversion = (hired / total * 100) if total > 0 else 0
            source_success.append(conversion)
        
        fig_heatmap = go.Figure(data=go.Heatmap(
            z=[source_success],
            x=sources,
            y=['Conversion Rate'],
            colorscale='RdYlGn',
            text=[[f"{s:.1f}%" for s in source_success]],
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        fig_heatmap.update_layout(title="Source Conversion Rates", height=300)
        
        return {
            "funnel": fig_funnel,
            "department": fig_dept,
            "scores": fig_scores,
            "heatmap": fig_heatmap
        }
    
    def export_to_excel(self, filename: str = "recruitment_report.xlsx") -> bytes:
        """Export all data to Excel with multiple sheets"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: All candidates
            df_candidates = pd.DataFrame(self.candidates)
            df_candidates.to_excel(writer, sheet_name='All Candidates', index=False)
            
            # Sheet 2: Jobs
            df_jobs = pd.DataFrame([job for job in self.jobs.values()])
            df_jobs.to_excel(writer, sheet_name='Jobs', index=False)
            
            # Sheet 3: Summary metrics
            internal = self.analytics.get_internal_metrics()
            external = self.analytics.get_external_metrics()
            referrals = self.analytics.get_referral_metrics()
            agency = self.analytics.get_agency_metrics()
            
            summary_data = {
                'Metric': ['Internal Applications', 'Internal Hires', 'Internal Conversion %',
                          'External Applications', 'External Hires', 'External Conversion %',
                          'Total Referrals', 'Successful Referrals', 'Referral Conversion %',
                          'Agencies', 'Proposed Candidates', 'Successful Placements', 'Placement Rate %'],
                'Value': [internal['applications'], internal['hires'], internal['conversion'],
                         external['applications'], external['hires'], external['conversion'],
                         referrals['total_referrals'], referrals['successful'], referrals['conversion'],
                         agency['agencies'], agency['proposed_candidates'], agency['successful_placements'], 
                         agency['placement_rate']]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Summary', index=False)
            
            # Sheet 4: Department breakdown
            dept_data = self.analytics.get_hires_by_department()
            df_dept = pd.DataFrame(list(dept_data.items()), columns=['Department', 'Percentage'])
            df_dept.to_excel(writer, sheet_name='By Department', index=False)
            
            # Sheet 5: Paygrade breakdown
            paygrade_data = self.analytics.get_hires_by_paygrade()
            df_paygrade = pd.DataFrame(list(paygrade_data.items()), columns=['Paygrade', 'Percentage'])
            df_paygrade.to_excel(writer, sheet_name='By Paygrade', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    def generate_pdf_report(self, filename: str = "recruitment_report.pdf") -> bytes:
        """Generate professional PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                     fontSize=24, textColor=colors.HexColor('#2E4053'))
        story.append(Paragraph("Recruitment Dashboard Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Date
        date_style = ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, textColor=colors.grey)
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", date_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary metrics table
        internal = self.analytics.get_internal_metrics()
        external = self.analytics.get_external_metrics()
        referrals = self.analytics.get_referral_metrics()
        agency = self.analytics.get_agency_metrics()
        
        summary_data = [
            ['Metric', 'Applications', 'Hires', 'Conversion Rate'],
            ['Internal', internal['applications'], internal['hires'], f"{internal['conversion']}%"],
            ['External', external['applications'], external['hires'], f"{external['conversion']}%"],
            ['Referrals', referrals['total_referrals'], referrals['successful'], f"{referrals['conversion']}%"],
            ['Agency', agency['proposed_candidates'], agency['successful_placements'], f"{agency['placement_rate']}%"]
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4053')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Department distribution
        story.append(Paragraph("Hires by Department", styles['Heading2']))
        dept_data = self.analytics.get_hires_by_department()
        dept_table_data = [['Department', 'Percentage']]
        for dept, pct in dept_data.items():
            dept_table_data.append([dept, f"{pct}%"])
        
        dept_table = Table(dept_table_data)
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5D6D7E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(dept_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()


def create_timeline_chart(candidates: list) -> go.Figure:
    """Create hiring timeline chart"""
    # Group hires by month (simplified - using mock dates)
    import random
    from datetime import datetime, timedelta
    
    # Generate mock hire dates for demonstration
    hires = [c for c in candidates if c['status'] == 'hired']
    start_date = datetime(2024, 1, 1)
    hire_dates = [start_date + timedelta(days=random.randint(0, 365)) for _ in hires]
    
    # Count by month
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_counts = [0] * 12
    
    for date in hire_dates:
        monthly_counts[date.month - 1] += 1
    
    fig = go.Figure(data=go.Scatter(x=months, y=monthly_counts, mode='lines+markers',
                                    line=dict(color='darkblue', width=3),
                                    marker=dict(size=10, color='red')))
    fig.update_layout(title="Hiring Timeline",
                      xaxis_title="Month",
                      yaxis_title="Number of Hires",
                      height=400)
    
    return fig