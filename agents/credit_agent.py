from crewai import Agent
from crewai.tools import tool
from utils.rules import assess_credit_score

@tool
def credit_assessment_tool(applicant_data: dict):
    """Assess credit score using BFSI expertise"""
    return assess_credit_score(applicant_data.get('credit_score', 0))

credit_agent = Agent(
    role="Credit Assessment Agent",
    goal="Evaluate creditworthiness using credit scoring rules",
    backstory="""You are a highly experienced credit analyst with over 12 years of experience in 
    risk assessment and credit scoring. You have worked with leading credit bureaus and financial 
    institutions, developing expertise in interpreting credit scores, understanding credit history 
    patterns, and assessing repayment capacity. Your analytical skills help identify creditworthy 
    applicants while flagging potential credit risks. You understand the nuances of credit scoring 
    models and can provide comprehensive insights into an applicant's financial reliability.""",
    tools=[credit_assessment_tool],
    verbose=True,
    allow_delegation=False,
    llm="gemini-2.0-flash"
)
