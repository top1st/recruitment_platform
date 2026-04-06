import pandas as pd
from collections import defaultdict
from typing import Dict, List

class HiringAnalytics:
    def __init__(self, candidates: List[dict], jobs: dict):
        self.candidates = candidates
        self.jobs = jobs
    
    def get_internal_metrics(self) -> dict:
        internal = [c for c in self.candidates if c.get("source") == "internal"]
        hires = [c for c in internal if c.get("status") == "hired"]
        conversion = (len(hires) / len(internal) * 100) if internal else 0
        
        return {
            "applications": len(internal),
            "hires": len(hires),
            "conversion": round(conversion, 1)
        }
    
    def get_external_metrics(self) -> dict:
        external = [c for c in self.candidates if c.get("source") == "external"]
        hires = [c for c in external if c.get("status") == "hired"]
        conversion = (len(hires) / len(external) * 100) if external else 0
        
        return {
            "applications": len(external),
            "hires": len(hires),
            "conversion": round(conversion, 1)
        }
    
    def get_referral_metrics(self) -> dict:
        referrals = [c for c in self.candidates if c.get("source") == "referral"]
        hires = [c for c in referrals if c.get("status") == "hired"]
        conversion = (len(hires) / len(referrals) * 100) if referrals else 0
        
        return {
            "total_referrals": len(referrals),
            "successful": len(hires),
            "conversion": round(conversion, 1)
        }
    
    def get_agency_metrics(self) -> dict:
        agency = [c for c in self.candidates if c.get("source") == "agency"]
        hires = [c for c in agency if c.get("status") == "hired"]
        placement_rate = (len(hires) / len(agency) * 100) if agency else 0
        
        # Count unique agencies (simplified - assumes agency name in candidate)
        agencies = set([c.get("agency_name", "Unknown") for c in agency if c.get("agency_name")])
        
        return {
            "agencies": len(agencies),
            "proposed_candidates": len(agency),
            "successful_placements": len(hires),
            "placement_rate": round(placement_rate, 1)
        }
    
    def get_hires_by_department(self) -> dict:
        """Distribution of hired candidates by department"""
        hires = [c for c in self.candidates if c.get("status") == "hired"]
        dept_counts = defaultdict(int)
        
        for hire in hires:
            job_id = hire.get("job_id")
            if job_id and job_id in self.jobs:
                dept = self.jobs[job_id].get("dept", "Unknown")
                dept_counts[dept] += 1
        
        # Convert to percentages
        total = sum(dept_counts.values())
        if total > 0:
            for dept in dept_counts:
                dept_counts[dept] = round(dept_counts[dept] / total * 100, 2) # type: ignore
        
        return dict(dept_counts)
    
    def get_hires_by_paygrade(self) -> dict:
        """Distribution of hired candidates by paygrade"""
        hires = [c for c in self.candidates if c.get("status") == "hired"]
        paygrade_counts = defaultdict(int)
        
        for hire in hires:
            job_id = hire.get("job_id")
            if job_id and job_id in self.jobs:
                paygrade = self.jobs[job_id].get("paygrade", "Unknown")
                paygrade_counts[paygrade] += 1
        
        total = sum(paygrade_counts.values())
        if total > 0:
            for grade in paygrade_counts:
                paygrade_counts[grade] = round(paygrade_counts[grade] / total * 100, 2) # type: ignore
        
        return dict(paygrade_counts)
    
    def get_referrals_by_department(self) -> dict:
        """Referrals broken down by department"""
        referrals = [c for c in self.candidates if c.get("source") == "referral"]
        dept_counts = defaultdict(int)
        
        for ref in referrals:
            job_id = ref.get("job_id")
            if job_id and job_id in self.jobs:
                dept = self.jobs[job_id].get("dept", "Unknown")
                dept_counts[dept] += 1
        
        return dict(dept_counts)
    
    def generate_full_report(self) -> dict:
        """Generate all metrics in one dictionary"""
        return {
            "internal": self.get_internal_metrics(),
            "external": self.get_external_metrics(),
            "referrals": self.get_referral_metrics(),
            "agency": self.get_agency_metrics(),
            "by_department": self.get_hires_by_department(),
            "by_paygrade": self.get_hires_by_paygrade(),
            "referrals_by_dept": self.get_referrals_by_department()
        }
    
    def print_dashboard(self):
        """Print a text-based dashboard similar to your image"""
        report = self.generate_full_report()
        
        print("\n" + "="*60)
        print("HIRING DASHBOARD - Internal & External Hires Distribution")
        print("="*60)
        
        print("\n📊 CANDIDATE METRICS")
        print("-"*40)
        print(f"Internal Candidates:  {report['internal']['applications']} applications → {report['internal']['hires']} hires ({report['internal']['conversion']}% conversion)")
        print(f"External Candidates:  {report['external']['applications']} applications → {report['external']['hires']} hires ({report['external']['conversion']}% conversion)")
        print(f"Employee Referrals:   {report['referrals']['total_referrals']} referrals → {report['referrals']['successful']} hires ({report['referrals']['conversion']}% conversion)")
        print(f"Agency Placements:    {report['agency']['agencies']} agencies, {report['agency']['proposed_candidates']} proposed → {report['agency']['successful_placements']} placements ({report['agency']['placement_rate']}% rate)")
        
        print("\n🏢 HIRES DISTRIBUTION BY DEPARTMENT")
        print("-"*40)
        for dept, pct in sorted(report['by_department'].items(), key=lambda x: x[1], reverse=True):
            print(f"{dept}: {pct}%")
        
        print("\n💰 HIRES DISTRIBUTION BY PAYGRADE")
        print("-"*40)
        for grade, pct in sorted(report['by_paygrade'].items(), key=lambda x: x[1], reverse=True):
            print(f"{grade}: {pct}%")
        
        print("\n👥 REFERRALS BY DEPARTMENT")
        print("-"*40)
        for dept, count in sorted(report['referrals_by_dept'].items(), key=lambda x: x[1], reverse=True):
            print(f"{dept}: {count}")
        
        print("\n" + "="*60)