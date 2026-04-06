from data import jobs, candidates
from analytics import HiringAnalytics

analytics = HiringAnalytics(candidates, jobs)
analytics.print_dashboard()

# Get raw data for frontend
report = analytics.generate_full_report()
print("\n📈 Raw metrics for API/frontend:")
print(report)