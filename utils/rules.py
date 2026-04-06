"""
BFSI Business Rules for Loan Processing System

This module contains all the business logic and validation rules
for the intelligent loan processing system.
"""

from typing import Dict, Tuple, Literal
from enum import Enum
from .logger import get_logger, log_decorator

class CreditRating(Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    MEDIUM = "Medium"
    POOR = "Poor"


class RiskLevel(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class LoanStatus(Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"
    REVIEW = "Review"


@log_decorator()
def validate_kyc(applicant_data: Dict) -> Tuple[bool, str]:
    """
    KYC Validation Rules
    
    Args:
        applicant_data: Dictionary containing applicant information
        
    Returns:
        Tuple of (is_valid, reason)
    """
    logger = get_logger()
    logger.log_business_rule_execution("validate_kyc", applicant_data, {})
    age = applicant_data.get('age', 0)
    
    # Rule: Reject if age < 18
    if age < 18:
        return False, f"Applicant is underage ({age} years old). Minimum age requirement is 18."
    
    # Rule: Check for reasonable age range
    if age > 100:
        return False, f"Invalid age provided ({age} years old)."
    
    # Rule: Validate required fields
    required_fields = ['name', 'age', 'income', 'loan_amount']
    missing_fields = [field for field in required_fields if not applicant_data.get(field)]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Rule: Validate income is positive
    income = applicant_data.get('income', 0)
    if income <= 0:
        return False, f"Invalid income amount: {income}. Income must be positive."
    
    # Rule: Validate loan amount is positive and reasonable
    loan_amount = applicant_data.get('loan_amount', 0)
    if loan_amount <= 0:
        return False, f"Invalid loan amount: {loan_amount}. Loan amount must be positive."
    
    if loan_amount > 10000000:  # 1 crore limit
        return False, f"Loan amount {loan_amount} exceeds maximum limit of 1 crore."
    
    result = (True, "KYC validation passed successfully.")
    logger.log_business_rule_execution("validate_kyc", applicant_data, {"result": result[0], "reason": result[1]})
    return result


@log_decorator()
def assess_credit_score(credit_score: int) -> Tuple[CreditRating, str]:
    """
    Credit Score Assessment
    
    Args:
        credit_score: Applicant's credit score
        
    Returns:
        Tuple of (rating, explanation)
    """
    logger = get_logger()
    inputs = {"credit_score": credit_score}
    if credit_score > 850:
        return CreditRating.EXCELLENT, f"Exceptional credit score of {credit_score}. Very low credit risk."
    
    elif credit_score > 700:
        return CreditRating.GOOD, f"Good credit score of {credit_score}. Low to moderate credit risk."
    
    elif credit_score >= 600:
        return CreditRating.MEDIUM, f"Fair credit score of {credit_score}. Moderate credit risk."
    
    else:
        result = (CreditRating.POOR, f"Poor credit score of {credit_score}. High credit risk.")
    
    logger.log_business_rule_execution("assess_credit_score", inputs, {"rating": result[0].value, "explanation": result[1]})
    return result


def calculate_risk_level(applicant_data: Dict, credit_rating: CreditRating) -> Tuple[RiskLevel, str]:
    """
    Risk Assessment based on multiple factors
    
    Args:
        applicant_data: Dictionary containing applicant information
        credit_rating: Credit rating from credit assessment
        
    Returns:
        Tuple of (risk_level, explanation)
    """
    income = applicant_data.get('income', 0)
    loan_amount = applicant_data.get('loan_amount', 0)
    existing_loans = applicant_data.get('existing_loans', 0)
    age = applicant_data.get('age', 0)
    
    risk_factors = []
    risk_score = 0
    
    # Rule: High risk if loan_amount > 5x income
    loan_to_income_ratio = loan_amount / income if income > 0 else float('inf')
    if loan_to_income_ratio > 5:
        risk_factors.append(f"Loan amount ({loan_amount}) is {loan_to_income_ratio:.1f}x annual income")
        risk_score += 3
    elif loan_to_income_ratio > 3:
        risk_factors.append(f"Loan amount ({loan_amount}) is {loan_to_income_ratio:.1f}x annual income")
        risk_score += 1
    
    # Rule: High risk if existing_loans > 2
    if existing_loans > 2:
        risk_factors.append(f"Applicant has {existing_loans} existing loans")
        risk_score += 2
    elif existing_loans > 0:
        risk_factors.append(f"Applicant has {existing_loans} existing loan(s)")
        risk_score += 1
    
    # Rule: Consider credit rating
    if credit_rating == CreditRating.POOR:
        risk_factors.append("Poor credit rating")
        risk_score += 3
    elif credit_rating == CreditRating.MEDIUM:
        risk_factors.append("Medium credit rating")
        risk_score += 1
    
    # Rule: Age-based risk
    if age < 21:
        risk_factors.append(f"Young applicant ({age} years old)")
        risk_score += 1
    elif age > 60:
        risk_factors.append(f"Near retirement age ({age} years old)")
        risk_score += 1
    
    # Determine risk level
    if risk_score >= 5:
        risk_level = RiskLevel.HIGH
        explanation = f"High risk assessment. Risk factors: {'; '.join(risk_factors)}"
    elif risk_score >= 2:
        risk_level = RiskLevel.MEDIUM
        explanation = f"Medium risk assessment. Risk factors: {'; '.join(risk_factors)}"
    else:
        risk_level = RiskLevel.LOW
        if risk_factors:
            explanation = f"Low risk assessment. Minor considerations: {'; '.join(risk_factors)}"
        else:
            explanation = "Low risk assessment. Applicant meets all criteria comfortably."
    
    return risk_level, explanation


def detect_fraud(applicant_data: Dict) -> Tuple[bool, str]:
    """
    Fraud Detection Rules
    
    Args:
        applicant_data: Dictionary containing applicant information
        
    Returns:
        Tuple of (is_fraudulent, explanation)
    """
    income = applicant_data.get('income', 0)
    loan_amount = applicant_data.get('loan_amount', 0)
    credit_score = applicant_data.get('credit_score', 0)
    age = applicant_data.get('age', 0)
    
    fraud_indicators = []
    
    # Rule: Flag if very high loan with low income
    loan_to_income_ratio = loan_amount / income if income > 0 else float('inf')
    if income < 200000 and loan_amount > 5000000:  # Low income, very high loan
        fraud_indicators.append(f"Suspicious: High loan amount ({loan_amount}) with low income ({income})")
    
    if loan_to_income_ratio > 10:  # Extremely high ratio
        fraud_indicators.append(f"Suspicious: Loan amount is {loan_to_income_ratio:.1f}x annual income")
    
    # Rule: Inconsistent data patterns
    if credit_score > 800 and income < 100000:
        fraud_indicators.append(f"Inconsistent: Excellent credit score ({credit_score}) with very low income ({income})")
    
    if age < 21 and loan_amount > 2000000:
        fraud_indicators.append(f"Suspicious: Very young applicant ({age}) requesting large loan ({loan_amount})")
    
    # Rule: Round number patterns (potential fake data)
    if income in [100000, 200000, 300000, 400000, 500000] and loan_amount in [1000000, 2000000, 3000000, 5000000]:
        fraud_indicators.append("Suspicious: Both income and loan amount are round numbers")
    
    # Rule: Credit score inconsistencies
    if credit_score < 300 or credit_score > 900:
        fraud_indicators.append(f"Invalid credit score: {credit_score}")
    
    # Determine fraud likelihood
    if len(fraud_indicators) >= 2:
        return True, f"Multiple fraud indicators detected: {'; '.join(fraud_indicators)}"
    elif len(fraud_indicators) == 1:
        return False, f"Suspicious pattern detected: {fraud_indicators[0]} (requires manual review)"
    else:
        return False, "No fraud indicators detected."


def make_final_decision(
    kyc_valid: bool,
    credit_rating: CreditRating,
    risk_level: RiskLevel,
    fraud_detected: bool,
    applicant_data: Dict
) -> Tuple[LoanStatus, str]:
    """
    Final Decision Logic
    
    Args:
        kyc_valid: Whether KYC validation passed
        credit_rating: Credit rating assessment
        risk_level: Risk level assessment
        fraud_detected: Whether fraud was detected
        applicant_data: Original applicant data
        
    Returns:
        Tuple of (decision, reasoning)
    """
    reasons = []
    
    # Rule: Reject if KYC failed
    if not kyc_valid:
        return LoanStatus.REJECTED, "Application rejected: KYC validation failed."
    
    # Rule: Reject if fraud detected
    if fraud_detected:
        return LoanStatus.REJECTED, "Application rejected: Fraud indicators detected."
    
    # Rule: Reject if high risk
    if risk_level == RiskLevel.HIGH:
        reasons.append("High risk level detected")
        return LoanStatus.REJECTED, f"Application rejected: {'; '.join(reasons)}."
    
    # Rule: Approve if good credit + low risk
    if credit_rating in [CreditRating.EXCELLENT, CreditRating.GOOD] and risk_level == RiskLevel.LOW:
        reasons.append("Good credit rating")
        reasons.append("Low risk assessment")
        return LoanStatus.APPROVED, f"Application approved: {'; '.join(reasons)}."
    
    # Rule: Review for medium risk or medium credit
    if risk_level == RiskLevel.MEDIUM or credit_rating == CreditRating.MEDIUM:
        if risk_level == RiskLevel.MEDIUM:
            reasons.append("Medium risk level")
        if credit_rating == CreditRating.MEDIUM:
            reasons.append("Medium credit rating")
        return LoanStatus.REVIEW, f"Application requires manual review: {'; '.join(reasons)}."
    
    # Default case
    return LoanStatus.REVIEW, "Application requires manual review due to mixed factors."


def generate_loan_summary(applicant_data: Dict, decision: LoanStatus, reasoning: str) -> Dict:
    """
    Generate final loan decision summary
    
    Args:
        applicant_data: Original applicant data
        decision: Final loan decision
        reasoning: Decision reasoning
        
    Returns:
        Structured decision summary
    """
    return {
        "applicant_name": applicant_data.get('name', 'Unknown'),
        "loan_amount_requested": applicant_data.get('loan_amount', 0),
        "status": decision.value,
        "reason": reasoning,
        "risk_level": assess_credit_score(applicant_data.get('credit_score', 0))[1].split()[0] if applicant_data.get('credit_score') else "Unknown",
        "credit_score": applicant_data.get('credit_score', 'Not provided'),
        "income": applicant_data.get('income', 0),
        "age": applicant_data.get('age', 0)
    }