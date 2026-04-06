"""
Multi-Agent Loan Processing System - Full CrewAI Implementation

This is the main entry point for the complete multi-agent AI loan processing system.
It demonstrates the full pipeline with all specialized agents working together.
"""

import os
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import tool
from tasks.tasks import create_all_tasks

# Load env variables
load_dotenv()

def setup_environment():
    """Setup environment variables and configuration"""
    # Load environment variables
    load_dotenv()
    
    # Check for Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY not found in environment variables.")
        print("Please set your Gemini API key in a .env file:")
        print("GEMINI_API_KEY=your_gemini_api_key_here")
        print("\nYou can get an API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ Gemini API key found!")
    return True

def get_sample_applications():
    """Returns a list of sample loan applications for testing"""
    return [
        # Case 1: Good candidate - should be approved
        {
            "name": "Rahul Sharma",
            "age": 28,
            "income": 800000,
            "loan_amount": 1500000,
            "credit_score": 750,
            "existing_loans": 0
        },
        
        # Case 2: Medium risk - should go to review
        {
            "name": "Priya Patel",
            "age": 35,
            "income": 600000,
            "loan_amount": 2500000,
            "credit_score": 680,
            "existing_loans": 1
        },
        
        # Case 3: High risk - should be rejected
        {
            "name": "Amit Kumar",
            "age": 24,
            "income": 300000,
            "loan_amount": 2000000,
            "credit_score": 580,
            "existing_loans": 2
        },
        
        # Case 4: Underage - should be rejected
        {
            "name": "Sneha Reddy",
            "age": 17,
            "income": 400000,
            "loan_amount": 500000,
            "credit_score": 720,
            "existing_loans": 0
        },
        
        # Case 5: Suspicious pattern - potential fraud
        {
            "name": "Vijay Kumar",
            "age": 20,
            "income": 100000,
            "loan_amount": 5000000,
            "credit_score": 850,
            "existing_loans": 0
        },
        
        # Case 6: Excellent candidate - should be approved
        {
            "name": "Anjali Singh",
            "age": 32,
            "income": 1200000,
            "loan_amount": 2000000,
            "credit_score": 820,
            "existing_loans": 0
        },
        
        # Case 7: Near retirement - medium risk
        {
            "name": "Ramesh Gupta",
            "age": 62,
            "income": 500000,
            "loan_amount": 1500000,
            "credit_score": 710,
            "existing_loans": 1
        },
        
        # Case 8: High debt burden - should be rejected
        {
            "name": "Kavita Nair",
            "age": 30,
            "income": 400000,
            "loan_amount": 3000000,
            "credit_score": 650,
            "existing_loans": 3
        }
    ]

def print_header():
    """Print system header and introduction"""
    print("=" * 80)
    print("🏦 INTELLIGENT LOAN PROCESSING SYSTEM")
    print("=" * 80)
    print("Multi-Agent AI System for BFSI Loan Processing")
    print("Powered by CrewAI • Claude")
    print("=" * 80)
    print()

def print_application_summary(applications):
    """Print summary of applications to be processed"""
    print(f"📋 Processing {len(applications)} loan applications...")
    print()
    
    for i, app in enumerate(applications, 1):
        print(f"{i}. {app.get('name', 'Unknown')} - Age: {app.get('age')}, "
              f"Income: ₹{app.get('income'):,}, Loan: ₹{app.get('loan_amount'):,}, "
              f"Credit: {app.get('credit_score')}")
    
    print()

def print_detailed_result(result, app_number):
    """Print detailed result for a single application"""
    print(f"\n{'='*60}")
    print(f"APPLICATION #{app_number} RESULT")
    print(f"{'='*60}")
    
    print(f"👤 Applicant: {result.get('applicant_name', 'Unknown')}")
    print(f"💰 Loan Amount: ₹{result.get('loan_amount_requested', 0):,}")
    print(f"📊 Credit Score: {result.get('credit_score', 'N/A')}")
    print(f"💵 Annual Income: ₹{result.get('income', 0):,}")
    print(f"🎂 Age: {result.get('age', 'N/A')}")
    
    # Status with appropriate emoji
    status = result.get('status', 'Unknown')
    if status == 'Approved':
        status_emoji = "✅"
    elif status == 'Rejected':
        status_emoji = "❌"
    else:
        status_emoji = "⏳"
    
    print(f"\n{status_emoji} Decision: {status}")
    
    # Risk level with appropriate emoji
    risk = result.get('risk_level', 'Unknown')
    if risk == 'Low':
        risk_emoji = "🟢"
    elif risk == 'Medium':
        risk_emoji = "🟡"
    elif risk == 'High':
        risk_emoji = "🔴"
    else:
        risk_emoji = "⚪"
    
    print(f"{risk_emoji} Risk Level: {risk}")
    
    # Reason (truncate if too long)
    reason = result.get('reason', 'No reason provided')
    if len(reason) > 300:
        reason = reason[:300] + "..."
    
    print(f"\n📝 Reasoning:")
    print(f"   {reason}")
    
    # Error handling
    if result.get('error'):
        print(f"\n⚠️  Error occurred during processing")
    
    print(f"{'='*60}")

def print_summary_statistics(results):
    """Print summary statistics for all processed applications"""
    print(f"\n{'='*80}")
    print("📈 PROCESSING SUMMARY STATISTICS")
    print(f"{'='*80}")
    
    total = len(results)
    approved = sum(1 for r in results if r.get('status') == 'Approved')
    rejected = sum(1 for r in results if r.get('status') == 'Rejected')
    review = sum(1 for r in results if r.get('status') == 'Review')
    errors = sum(1 for r in results if r.get('error'))
    
    print(f"Total Applications Processed: {total}")
    print(f"✅ Approved: {approved} ({approved/total*100:.1f}%)")
    print(f"❌ Rejected: {rejected} ({rejected/total*100:.1f}%)")
    print(f"⏳ Manual Review: {review} ({review/total*100:.1f}%)")
    
    if errors > 0:
        print(f"⚠️  Errors: {errors} ({errors/total*100:.1f}%)")
    
    print(f"{'='*80}")

def save_results_to_file(results, filename=None):
    """Save results to a JSON file"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"loan_processing_results_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n💾 Results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"\n❌ Failed to save results: {e}")
        return None

def interactive_mode():
    """Interactive mode for custom loan applications"""
    print("\n" + "="*60)
    print("🎯 INTERACTIVE MODE - Custom Loan Application")
    print("="*60)
    
    try:
        print("\nEnter applicant details (press Enter for default values):")
        
        name = input("Name: ").strip() or "Test Applicant"
        age = int(input("Age: ").strip() or "25")
        income = int(input("Annual Income (₹): ").strip() or "500000")
        loan_amount = int(input("Loan Amount (₹): ").strip() or "300000")
        credit_score = int(input("Credit Score: ").strip() or "720")
        existing_loans = int(input("Existing Loans: ").strip() or "1")
        
        applicant_data = {
            "name": name,
            "age": age,
            "income": income,
            "loan_amount": loan_amount,
            "credit_score": credit_score,
            "existing_loans": existing_loans
        }
        
        print(f"\n🔄 Processing custom application for {name}...")
        result = quick_loan_process(applicant_data)
        print_detailed_result(result, "CUSTOM")
        
        return result
        
    except KeyboardInterrupt:
        print("\n\n👋 Interactive mode cancelled.")
        return None
    except ValueError as e:
        print(f"\n❌ Invalid input: {e}")
        return None
    except Exception as e:
        print(f"\n❌ Error processing application: {e}")
        return None

# -------------------------------
# ✅ MULTI-AGENT CREW SETUP
# -------------------------------
class LoanProcessingCrew:
    """
    Complete multi-agent crew for loan processing
    """
    
    def __init__(self):
        """Initialize the complete loan processing crew"""
        from agents.kyc_agent import kyc_agent
        from agents.credit_agent import credit_agent
        from agents.risk_agent import risk_agent
        from agents.fraud_agent import fraud_agent
        from agents.decision_agent import decision_agent
            
        self.agents = [kyc_agent, credit_agent, risk_agent, fraud_agent, decision_agent]
        self.tasks = create_all_tasks({})
            
        # Configure crew
        self.crew = Crew(
            agents=self.agents,
            process=Process.sequential,
            verbose=True,
            memory=False,
            max_rpm=100,
            tasks=self.tasks
        )
    
    def process_loan_application(self, applicant_data: dict) -> dict:
        """
        Process a loan application through the complete multi-agent pipeline
        
        Args:
            applicant_data: Dictionary containing applicant information
            
        Returns:
            Structured loan decision result
        """
        try:
            # Create all tasks for the pipeline
            tasks = create_all_tasks(applicant_data)
            
            # Update crew tasks dynamically
            self.crew.tasks = tasks
            
            # Execute crew
            result = self.crew.kickoff()
            
            # Parse and structure final result
            return self._parse_crew_result(result, applicant_data)
            
        except Exception as e:
            return {
                "status": "Error",
                "reason": f"Crew execution failed: {str(e)}",
                "risk_level": "Unknown",
                "error": True
            }
    
    def _parse_crew_result(self, crew_result, applicant_data: dict) -> dict:
        """
        Parse crew result and structure it properly
        
        Args:
            crew_result: Raw result from crew execution
            applicant_data: Original applicant data
            
        Returns:
            Structured loan decision
        """
        try:
            # Try to extract structured information from crew result
            result_text = str(crew_result)
            
            # Look for decision keywords
            decision_keywords = {
                "approved": "Approved",
                "rejected": "Rejected", 
                "review": "Review",
                "manual review": "Review"
            }
            
            # Extract decision status
            status = "Review"  # Default
            for keyword, decision in decision_keywords.items():
                if keyword.lower() in result_text.lower():
                    status = decision
                    break
            
            # Extract reasoning (take the full result as reasoning for now)
            reason = result_text
            
            # Extract risk level
            risk_keywords = ["low", "medium", "high"]
            risk_level = "Medium"  # Default
            for risk in risk_keywords:
                if f"{risk} risk" in result_text.lower() or f"{risk.capitalize()} risk" in result_text:
                    risk_level = risk.capitalize()
                    break
            
            # Generate structured summary
            return {
                "applicant_name": applicant_data.get('name', 'Unknown'),
                "loan_amount_requested": applicant_data.get('loan_amount', 0),
                "status": status,
                "reason": reason[:1000] if len(reason) > 1000 else reason,  # Limit reason length
                "risk_level": risk_level,
                "credit_score": applicant_data.get('credit_score', 'Not provided'),
                "income": applicant_data.get('income', 0),
                "age": applicant_data.get('age', 0),
                "existing_loans": applicant_data.get('existing_loans', 0),
                "crew_output": result_text  # Include full crew output for debugging
            }
            
        except Exception as e:
            return {
                "status": "Error",
                "reason": f"Result parsing failed: {str(e)}",
                "risk_level": "Unknown",
                "error": True,
                "crew_output": str(crew_result)
            }
    
    def process_multiple_applications(self, applications: list) -> list:
        """
        Process multiple loan applications
        
        Args:
            applications: List of applicant data dictionaries
            
        Returns:
            List of loan decision results
        """
        results = []
        
        for i, application in enumerate(applications):
            print(f"\n{'='*50}")
            print(f"Processing Application {i+1}/{len(applications)}")
            print(f"{'='*50}")
            
            result = self.process_loan_application(application)
            results.append(result)
            
            # Print summary for each application
            print(f"Applicant: {result.get('applicant_name', 'Unknown')}")
            print(f"Status: {result.get('status', 'Unknown')}")
            print(f"Risk Level: {result.get('risk_level', 'Unknown')}")
            print("-" * 50)
        
        return results

def create_loan_crew():
    """
    Factory function to create a new loan processing crew
    
    Returns:
        Configured LoanProcessingCrew instance
    """
    return LoanProcessingCrew()

def quick_loan_process(applicant_data: dict) -> dict:
    """
    Quick utility function to process a single loan application
    
    Args:
        applicant_data: Dictionary containing applicant information
        
    Returns:
        Structured loan decision result
    """
    crew = create_loan_crew()
    return crew.process_loan_application(applicant_data)

def main():
    """Main execution function"""
    # Print header
    print_header()
    
    # Setup environment
    if not setup_environment():
        print("\n❌ Cannot proceed without Claude API key")
        return
    
    # Get user choice
    print("Choose execution mode:")
    print("1. Process sample applications (8 test cases)")
    print("2. Interactive mode (custom application)")
    print("3. Both (sample applications + interactive)")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice not in ['1', '2', '3']:
            print("❌ Invalid choice. Defaulting to sample applications.")
            choice = '1'
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")
        return
    
    results = []
    
    # Process sample applications
    if choice in ['1', '3']:
        print("\n🚀 Starting sample application processing...")
        
        # Get sample applications
        applications = get_sample_applications()
        print_application_summary(applications)
        
        # Create crew and process applications
        crew = create_loan_crew()
        results = crew.process_multiple_applications(applications)
        
        # Print detailed results
        for i, result in enumerate(results, 1):
            print_detailed_result(result, i)
        
        # Print summary statistics
        print_summary_statistics(results)
        
        # Save results
        save_results_to_file(results)
    
    # Interactive mode
    if choice in ['2', '3']:
        interactive_result = interactive_mode()
        if interactive_result:
            results.append(interactive_result)
    
    print(f"\n🎉 Loan processing completed!")
    print(f"Total applications processed: {len(results)}")
    
    if choice in ['1', '3']:
        print("\n📊 Check the generated JSON file for detailed results.")

if __name__ == "__main__":
    main()
