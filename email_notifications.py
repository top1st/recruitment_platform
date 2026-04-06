import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import streamlit as st

class EmailNotifier:
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        """
        Initialize email notifier.
        Note: For production, use environment variables for credentials.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = None
        self.sender_password = None
    
    def configure(self, email: str, password: str):
        """Configure sender email credentials"""
        self.sender_email = email
        self.sender_password = password
    
    def send_candidate_response(self, candidate_email: str, candidate_name: str, 
                                job_title: str, match_score: float, 
                                status: str, interview_date: str = None) -> bool: # type: ignore
        """
        Send automated response to candidate based on screening result
        """
        if not self.sender_email:
            st.warning("Email not configured. Please add credentials in Settings.")
            return False
        
        if status == "shortlisted":
            subject = f"Interview Invitation: {job_title} at Our Company"
            body = f"""
            Dear {candidate_name},
            
            Congratulations! Based on your application for the {job_title} position, 
            you have been shortlisted for the next round.
            
            Match Score: {match_score}%
            
            {'Interview Date: ' + interview_date if interview_date else 'We will contact you shortly with interview details.'}
            
            Please reply to this email to confirm your availability.
            
            Best regards,
            Recruitment Team
            """
        elif status == "rejected":
            subject = f"Update on your application for {job_title}"
            body = f"""
            Dear {candidate_name},
            
            Thank you for your interest in the {job_title} position at our company.
            
            After careful review of your application (Match Score: {match_score}%), 
            we regret to inform you that you have not been selected for this position.
            
            However, we encourage you to apply for future openings that match your profile.
            
            We wish you the best in your job search.
            
            Best regards,
            Recruitment Team
            """
        else:  # screening in progress
            subject = f"Application Received: {job_title}"
            body = f"""
            Dear {candidate_name},
            
            Thank you for applying for the {job_title} position.
            
            Your application (Match Score: {match_score}%) is currently under review. 
            We will notify you once a decision has been made.
            
            Best regards,
            Recruitment Team
            """
        
        return self._send_email(candidate_email, subject, body)
    
    def send_interview_reminder(self, candidate_email: str, candidate_name: str,
                                job_title: str, interview_date: str, 
                                interview_link: str = None) -> bool: # type: ignore
        """Send interview reminder to candidate"""
        subject = f"Interview Reminder: {job_title}"
        body = f"""
        Dear {candidate_name},
        
        This is a reminder of your upcoming interview for the {job_title} position.
        
        Date & Time: {interview_date}
        {'Interview Link: ' + interview_link if interview_link else 'Location: Our Office, Room 301'}
        
        Please arrive 10 minutes before your scheduled time.
        
        Best regards,
        Recruitment Team
        """
        
        return self._send_email(candidate_email, subject, body)
    
    def send_bulk_updates(self, candidates: List[Dict], job_title: str, status: str) -> Dict:
        """Send bulk email updates to multiple candidates"""
        results = {"sent": 0, "failed": 0}
        
        for candidate in candidates:
            if candidate.get('email'):
                success = self.send_candidate_response(
                    candidate['email'],
                    candidate['name'],
                    job_title,
                    candidate.get('match_score', 0),
                    status
                )
                if success:
                    results["sent"] += 1
                else:
                    results["failed"] += 1
        
        return results
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Internal method to send email"""
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email # type: ignore
            msg["To"] = to_email
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            # Create SMTP session
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password) # type: ignore
                server.send_message(msg)
            
            return True
        
        except Exception as e:
            print(f"Error sending email to {to_email}: {str(e)}")
            return False


# Mock email for demo purposes (no actual sending)
class MockEmailNotifier:
    """Mock email notifier for demonstration without actual email configuration"""
    
    def configure(self, email: str, password: str):
        st.info(f"📧 Demo mode: Would send emails from {email}")
    
    def send_candidate_response(self, candidate_email: str, candidate_name: str, 
                                job_title: str, match_score: float, 
                                status: str, interview_date: str = None) -> bool: # type: ignore
        st.success(f"📧 [DEMO] Email sent to {candidate_email}")
        st.markdown(f"""
        **To:** {candidate_email}
        **Subject:** {status.upper()}: {job_title}
        
        Dear {candidate_name},
        
        Your application for {job_title} has been {status}.
        Match Score: {match_score}%
        
        [Full email content would be sent in production]
        """)
        return True
    
    def send_interview_reminder(self, candidate_email: str, candidate_name: str,
                                job_title: str, interview_date: str, 
                                interview_link: str = None) -> bool: # type: ignore
        st.success(f"📧 [DEMO] Interview reminder sent to {candidate_email}")
        return True
    
    def send_bulk_updates(self, candidates: List[Dict], job_title: str, status: str) -> Dict:
        st.info(f"📧 [DEMO] Would send {status} updates to {len(candidates)} candidates")
        return {"sent": len(candidates), "failed": 0}