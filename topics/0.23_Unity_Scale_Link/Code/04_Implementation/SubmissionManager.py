"""
UET Submission Manager - Submit papers and manage peer review
==========================================================
Topic: 0.23_Unity_Scale_Link
Folder: 04_Implementation

Submit papers to journals and manage peer review process
"""

import sys
from pathlib import Path
import time
import json
import random

# Path setup


from PaperGenerator import PaperGenerator

class SubmissionManager:
    """
    Manage paper submission and peer review
    """
    
    def __init__(self):
        self.paper_generator = PaperGenerator()
        self.submissions = []
        self.load_papers()
    
    def load_papers(self):
        """
        Load generated papers
        """
        papers_dir = Path(__file__).parent / "Results" / "Papers"
        
        self.papers = []
        for i in range(1, 5):
            paper_file = papers_dir / f"{i:02d}_*.json"
            for file in papers_dir.glob(f"{i:02d}_*.json"):
                with open(file, "r") as f:
                    paper = json.load(f)
                    paper["file"] = file
                    self.papers.append(paper)
    
    def submit_to_nature_physics(self, paper):
        """
        Submit paper to Nature Physics
        """
        submission = {
            "paper_id": paper["title"],
            "journal": "Nature Physics",
            "submission_date": time.strftime("%Y-%m-%d"),
            "status": "Submitted",
            "expected_review_time": "3-6 months",
            "impact_factor": 12.5,
            "acceptance_rate": 0.08,  # 8%
            "review_criteria": [
                "Novelty and significance",
                "Methodological rigor", 
                "Experimental validation",
                "Clarity of presentation"
            ]
        }
        
        # Simulate submission process
        print(f"📤 Submitting to Nature Physics...")
        print(f"   Title: {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   Date: {submission['submission_date']}")
        print(f"   Status: {submission['status']}")
        
        return submission
    
    def submit_to_physical_review_letters(self, paper):
        """
        Submit paper to Physical Review Letters
        """
        submission = {
            "paper_id": paper["title"],
            "journal": "Physical Review Letters",
            "submission_date": time.strftime("%Y-%m-%d"),
            "status": "Submitted",
            "expected_review_time": "2-4 months",
            "impact_factor": 8.8,
            "acceptance_rate": 0.25,  # 25%
            "review_criteria": [
                "Significant breakthrough",
                "Technical correctness",
                "Broad interest",
                "Concise presentation"
            ]
        }
        
        print(f"📤 Submitting to Physical Review Letters...")
        print(f"   Title: {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   Date: {submission['submission_date']}")
        print(f"   Status: {submission['status']}")
        
        return submission
    
    def submit_to_nature(self, paper):
        """
        Submit paper to Nature
        """
        submission = {
            "paper_id": paper["title"],
            "journal": "Nature",
            "submission_date": time.strftime("%Y-%m-%d"),
            "status": "Submitted", 
            "expected_review_time": "4-8 months",
            "impact_factor": 49.9,
            "acceptance_rate": 0.08,  # 8%
            "review_criteria": [
                "Outstanding significance",
                "Broad scientific interest",
                "Original research",
                "Rigorous methodology"
            ]
        }
        
        print(f"📤 Submitting to Nature...")
        print(f"   Title: {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   Date: {submission['submission_date']}")
        print(f"   Status: {submission['status']}")
        
        return submission
    
    def submit_to_physical_review_x(self, paper):
        """
        Submit paper to Physical Review X
        """
        submission = {
            "paper_id": paper["title"],
            "journal": "Physical Review X",
            "submission_date": time.strftime("%Y-%m-%d"),
            "status": "Submitted",
            "expected_review_time": "3-6 months", 
            "impact_factor": 5.5,
            "acceptance_rate": 0.30,  # 30%
            "review_criteria": [
                "High quality and significance",
                "Technical excellence",
                "Interdisciplinary interest",
                "Comprehensive coverage"
            ]
        }
        
        print(f"📤 Submitting to Physical Review X...")
        print(f"   Title: {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   Date: {submission['submission_date']}")
        print(f"   Status: {submission['status']}")
        
        return submission
    
    def simulate_peer_review(self, submission):
        """
        Simulate peer review process
        """
        # Simulate review time
        review_time = random.randint(1, 8)  # months
        time.sleep(0.1)  # Brief pause for effect
        
        # Simulate review outcome based on acceptance rate
        acceptance_prob = submission["acceptance_rate"]
        outcome = "Accepted" if random.random() < acceptance_prob else "Rejected"
        
        # Generate reviewer comments
        if outcome == "Accepted":
            comments = [
                "Excellent work with significant contributions",
                "Rigorous methodology and clear presentation", 
                "Novel approach with broad implications",
                "Strong experimental validation"
            ]
        else:
            comments = [
                "Interesting but requires additional validation",
                "Methodology needs further clarification",
                "Claims exceed current evidence",
                "Requires comparison with existing theories"
            ]
        
        review_result = {
            "submission": submission,
            "review_time_months": review_time,
            "outcome": outcome,
            "reviewer_comments": random.sample(comments, 2),
            "decision_date": time.strftime("%Y-%m-%d")
        }
        
        return review_result
    
    def submit_all_papers(self):
        """
        Submit all papers to appropriate journals
        """
        print("=" * 80)
        print("📤 UET SUBMISSION MANAGER - TOP JOURNALS")
        print("=" * 80)
        
        submissions = []
        
        # Map papers to journals
        journal_mapping = {
            0: self.submit_to_nature_physics,      # Landauer paper
            1: self.submit_to_physical_review_letters,  # Thermodynamic paper
            2: self.submit_to_nature,             # Cross-domain paper
            3: self.submit_to_physical_review_x   # Mathematical rigor paper
        }
        
        for i, paper in enumerate(self.papers):
            print(f"\n[{i+1}/4] Submitting Paper {i+1}")
            
            # Submit to appropriate journal
            submit_func = journal_mapping[i]
            submission = submit_func(paper)
            submissions.append(submission)
            
            print(f"   ✅ Submitted to {submission['journal']}")
            print(f"   📊 Impact Factor: {submission['impact_factor']}")
            print(f"   📈 Acceptance Rate: {submission['acceptance_rate']*100:.1f}%")
        
        return submissions
    
    def run_peer_review_simulation(self, submissions):
        """
        Run peer review simulation
        """
        print(f"\n{'='*80}")
        print("🔍 PEER REVIEW SIMULATION")
        print(f"{'='*80}")
        
        review_results = []
        
        for i, submission in enumerate(submissions):
            print(f"\n[{i+1}/4] Reviewing Paper {i+1}")
            print(f"   Journal: {submission['journal']}")
            print(f"   Title: {submission['paper_id'][:50]}...")
            
            # Simulate review
            result = self.simulate_peer_review(submission)
            review_results.append(result)
            
            print(f"   ⏱️  Review Time: {result['review_time_months']} months")
            print(f"   📋 Outcome: {result['outcome']}")
            print(f"   💬 Reviewer Comments:")
            for comment in result['reviewer_comments']:
                print(f"      • {comment}")
        
        return review_results
    
    def generate_submission_report(self, submissions, review_results):
        """
        Generate comprehensive submission report
        """
        print(f"\n{'='*80}")
        print("📊 SUBMISSION REPORT")
        print(f"{'='*80}")
        
        # Calculate statistics
        total_submissions = len(submissions)
        accepted = sum(1 for r in review_results if r['outcome'] == 'Accepted')
        rejected = total_submissions - accepted
        acceptance_rate = accepted / total_submissions * 100
        
        # Calculate impact factors
        total_impact = sum(s['impact_factor'] for s in submissions)
        avg_impact = total_impact / total_submissions
        
        print(f"Total Submissions: {total_submissions}")
        print(f"Accepted: {accepted}")
        print(f"Rejected: {rejected}")
        print(f"Acceptance Rate: {acceptance_rate:.1f}%")
        print(f"Average Impact Factor: {avg_impact:.1f}")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        for i, (submission, result) in enumerate(zip(submissions, review_results)):
            status_icon = "✅" if result['outcome'] == 'Accepted' else "❌"
            print(f"\n{status_icon} Paper {i+1}: {submission['journal']}")
            print(f"   Title: {submission['paper_id'][:50]}...")
            print(f"   Outcome: {result['outcome']}")
            print(f"   Review Time: {result['review_time_months']} months")
            print(f"   Impact Factor: {submission['impact_factor']}")
        
        # Save report
        output_dir = Path(__file__).parent / "Results" / "Submissions"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "submissions": submissions,
            "review_results": review_results,
            "statistics": {
                "total_submissions": total_submissions,
                "accepted": accepted,
                "rejected": rejected,
                "acceptance_rate": acceptance_rate,
                "average_impact_factor": avg_impact
            }
        }
        
        with open(output_dir / "submission_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {output_dir / 'submission_report.json'}")
        
        return report


def test_submission_manager():
    """
    Test the submission manager
    """
    manager = SubmissionManager()
    
    # Submit all papers
    submissions = manager.submit_all_papers()
    
    # Run peer review simulation
    review_results = manager.run_peer_review_simulation(submissions)
    
    # Generate report
    report = manager.generate_submission_report(submissions, review_results)
    
    return manager, submissions, review_results, report


if __name__ == "__main__":
    manager, submissions, review_results, report = test_submission_manager()
