from crewai import Task
from agents.kyc_agent import kyc_agent
from agents.credit_agent import credit_agent
from agents.risk_agent import risk_agent
from agents.fraud_agent import fraud_agent
from agents.decision_agent import decision_agent


def create_all_tasks(applicant_data: dict):

    # 🔹 1. KYC TASK
    kyc_task = Task(
        description=f"""
        Perform KYC verification.

        Applicant Data:
        {applicant_data}

        Instructions:
        - You MUST use kyc_validation_tool
        - Validate all fields strictly using rules
        - Do NOT rely only on reasoning

        Return ONLY JSON:
        {{
            "kyc_valid": true/false,
            "reason": "explanation"
        }}
        """,
        agent=kyc_agent,
        expected_output="JSON with kyc_valid and reason"
    )

    # 🔹 2. CREDIT TASK
    credit_task = Task(
        description=f"""
        Perform credit assessment.

        Applicant Data:
        {applicant_data}

        Instructions:
        - You MUST use credit_assessment_tool
        - Evaluate credit score: {applicant_data.get('credit_score')}
        - Consider KYC result from previous task

        Return ONLY JSON:
        {{
            "credit_rating": "Excellent/Good/Medium/Poor",
            "reason": "explanation"
        }}
        """,
        agent=credit_agent,
        context=[kyc_task],   # ✅ REAL DEPENDENCY
        expected_output="JSON with credit_rating and reason"
    )

    # 🔹 3. RISK TASK
    risk_task = Task(
        description=f"""
        Perform risk assessment.

        Applicant Data:
        {applicant_data}

        Instructions:
        - You MUST use risk_assessment_tool
        - Use credit_rating from previous task
        - Analyze income, loan amount, existing loans

        Return ONLY JSON:
        {{
            "risk_level": "Low/Medium/High",
            "reason": "explanation"
        }}
        """,
        agent=risk_agent,
        context=[kyc_task, credit_task],   # ✅ REAL FLOW
        expected_output="JSON with risk_level and reason"
    )

    # 🔹 4. FRAUD TASK
    fraud_task = Task(
        description=f"""
        Perform fraud detection.

        Applicant Data:
        {applicant_data}

        Instructions:
        - You MUST use fraud_detection_tool
        - Identify suspicious patterns
        - Use previous outputs if needed

        Return ONLY JSON:
        {{
            "fraud_detected": true/false,
            "reason": "explanation"
        }}
        """,
        agent=fraud_agent,
        context=[kyc_task, credit_task, risk_task],
        expected_output="JSON with fraud_detected and reason"
    )

    # 🔹 5. DECISION TASK
    decision_task = Task(
        description=f"""
        Make final loan decision.

        Applicant Data:
        {applicant_data}

        Instructions:
        - You MUST use decision_tool
        - Use ALL previous outputs:
            - kyc_valid
            - credit_rating
            - risk_level
            - fraud_detected
        - Apply BFSI rules strictly

        Return ONLY JSON (NO extra text):
        {{
            "status": "Approved/Rejected/Review",
            "reason": "clear explanation",
            "risk_level": "Low/Medium/High"
        }}
        """,
        agent=decision_agent,
        context=[kyc_task, credit_task, risk_task, fraud_task],
        expected_output="Final structured JSON decision"
    )

    return [kyc_task, credit_task, risk_task, fraud_task, decision_task]