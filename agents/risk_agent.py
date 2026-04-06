from crewai import Agent
from crewai.tools import tool
from utils.rules import calculate_risk_level, CreditRating

@tool
def risk_assessment_tool(applicant_data: dict):
    """Calculate risk level using BFSI expertise"""
    credit_rating = CreditRating(applicant_data.get('credit_rating', 'MEDIUM'))
    return calculate_risk_level(applicant_data, credit_rating)

risk_agent = Agent(
    role="Risk Assessment Agent",
    goal="Assess loan risk using financial rules",
    backstory="""You are a senior risk assessment specialist with 14 years of experience in banking 
    and financial risk management. You have developed sophisticated risk models for major financial 
    institutions and have a deep understanding of loan-to-income ratios, debt-to-income ratios, 
    and other critical risk metrics. Your expertise lies in identifying potential default risks 
    by analyzing income stability, existing debt obligations, age factors, and economic conditions. 
    You are skilled at quantifying risk levels and providing actionable insights to support 
    informed lending decisions.""",
    tools=[risk_assessment_tool],
    verbose=True,
    allow_delegation=False,
    llm="gemini-2.0-flash"
)