from crewai import Agent
from crewai.tools import tool
from utils.rules import validate_kyc

@tool
def kyc_validation_tool(applicant_data: dict):
    """Validate KYC details of applicant"""
    return validate_kyc(applicant_data)

kyc_agent = Agent(
    role="KYC Verification Agent",
    goal="Verify user identity using strict BFSI validation rules",
    backstory="""You are a seasoned KYC (Know Your Customer) specialist with over 15 years of experience 
    in banking and financial services. You have worked with major banks and financial institutions, 
    verifying thousands of customer identities. You are meticulous, detail-oriented, and well-versed 
    in regulatory requirements including age restrictions, documentation validation, and identity 
    verification protocols. Your expertise ensures that only legitimate applications proceed to the 
    next stage of the loan processing pipeline.""",
    tools=[kyc_validation_tool],
    verbose=True,
    allow_delegation=False,
    llm="gemini-2.0-flash"
)