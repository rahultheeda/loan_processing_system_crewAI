from crewai import Agent
from crewai.tools import tool
from utils.rules import make_final_decision, LoanStatus, CreditRating, RiskLevel

@tool
def decision_tool(kyc_valid: bool, credit: str, risk: str, fraud: bool, applicant_data: dict):
    """Make final loan decision using BFSI expertise"""
    return make_final_decision(
        kyc_valid,
        CreditRating(credit),
        RiskLevel(risk),
        fraud,
        applicant_data
    )

decision_agent = Agent(
    role="Loan Decision Agent",
    goal="Make final decision using strict BFSI rules",
    backstory="""You are a senior loan approval manager with 18 years of experience in banking 
    and financial services. You have authority to make final lending decisions and have 
    successfully managed loan portfolios worth billions of dollars. Your expertise combines 
    deep understanding of credit risk, regulatory compliance, and business strategy. You are 
    known for making balanced, data-driven decisions that protect the institution's interests 
    while maintaining fair lending practices. You excel at synthesizing complex information 
    from multiple sources and making clear, well-reasoned decisions that align with 
    the organization's risk appetite and business objectives.""",
    tools=[decision_tool],
    verbose=True,
    allow_delegation=False,
    llm="gemini-2.0-flash"
)