# 🏦 Intelligent Loan Processing System

A multi-agent AI system for BFSI loan processing using CrewAI and Google Gemini.

## 🚀 Features

- **Multi-Agent Architecture**: 5 specialized agents for complete loan processing
- **Google Gemini Integration**: Latest Google GenAI SDK with API key authentication
- **BFSI Compliance**: Banking and financial services industry standards
- **Risk Assessment**: Comprehensive credit, risk, and fraud analysis
- **Automated Decision Making**: Data-driven loan approval/rejection decisions

## 🏗️ Architecture

### Agents

1. **KYC Agent** - Identity verification and compliance checks
2. **Credit Agent** - Credit score assessment and analysis
3. **Risk Agent** - Risk level calculation and evaluation
4. **Fraud Agent** - Fraud detection and pattern analysis
5. **Decision Agent** - Final loan decision making

### Technology Stack

- **Framework**: CrewAI
- **LLM**: Google Gemini 2.0 Flash
- **Language**: Python 3.9+
- **API**: Google GenAI SDK (latest)

## 📋 Prerequisites

- Python 3.9 or higher
- Google Gemini API key
- Virtual environment (recommended)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd loan_processing_system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv loan_env
   source loan_env/bin/activate  # On Windows: loan_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # For Windows
   setx GEMINI_API_KEY "your_gemini_api_key_here"
   
   # For Mac/Linux
   export GEMINI_API_KEY="your_gemini_api_key_here"
   ```

5. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env file with your API key
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Model Configuration
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.1

# Logging Configuration
LOG_LEVEL=INFO
LOG_NAME=loan_processing

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
```

### Getting Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and add it to your `.env` file

## 🚀 Usage

### Running the System

1. **Interactive Mode**
   ```bash
   python main.py
   ```
   Choose from:
   - Process sample applications
   - Interactive mode (custom application)
   - Both

2. **Quick Processing**
   ```python
   from main import quick_loan_process
   
   applicant = {
       "name": "John Doe",
       "age": 30,
       "income": 75000,
       "loan_amount": 25000,
       "credit_score": 720,
       "existing_loans": 1
   }
   
   result = quick_loan_process(applicant)
   print(result)
   ```

3. **API Server**
   ```bash
   python api.py
   ```
   Access at: `http://localhost:8000`

### Sample Input Format

```json
{
  "name": "Rahul Sharma",
  "age": 28,
  "income": 800000,
  "loan_amount": 1500000,
  "credit_score": 750,
  "existing_loans": 0
}
```

### Sample Output

```json
{
  "applicant_name": "Rahul Sharma",
  "status": "Approved",
  "reason": "Good credit score, stable income, low risk factors",
  "risk_level": "Low",
  "credit_score": 750,
  "income": 800000,
  "age": 28,
  "loan_amount_requested": 1500000
}
```

## 📊 Business Logic

### KYC Validation Rules
- Age must be between 18-100 years
- Income must be positive
- Credit score must be between 300-900

### Credit Assessment
- **Excellent** (750+): Very low credit risk
- **Good** (700-749): Low to moderate credit risk
- **Medium** (600-699): Moderate credit risk
- **Poor** (<600): High credit risk

### Risk Factors
- Loan-to-income ratio > 5x: High risk
- Existing loans > 2: Increased risk
- Age < 25 or > 60: Moderate risk

### Fraud Detection
- Suspicious data patterns
- Inconsistent information
- Unusual financial behaviors

## 🧪 Testing

### Run Sample Applications
```bash
python main.py
# Choose option 1 to run 8 sample test cases
```

### Test Custom Application
```bash
python main.py
# Choose option 2 for interactive mode
```

## 📝 API Documentation

### Endpoints

- `POST /process` - Process loan application
- `GET /health` - Health check
- `GET /agents` - List all agents
- `GET /results/{id}` - Get processing results

### Example API Call

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 30,
    "income": 75000,
    "loan_amount": 25000,
    "credit_score": 720,
    "existing_loans": 1
  }'
```

## 🔍 Monitoring & Logging

- Logs stored in `logs/` directory
- Structured JSON logging
- Error tracking and debugging
- Performance metrics

## 🚀 Deployment

### Docker Deployment
```bash
docker build -t loan-processing .
docker run -p 8000:8000 loan-processing
```

### Environment Setup
- Production: Use environment variables
- Development: Use .env file
- Testing: Mock API responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation

## 🔧 Troubleshooting

### Common Issues

1. **API Key Error**
   - Ensure GEMINI_API_KEY is set in .env
   - Check API key validity
   - Verify network connectivity

2. **Model Not Found**
   - Ensure correct model name: `gemini-2.0-flash`
   - Check API version: `v1beta`

3. **Import Errors**
   - Install all dependencies: `pip install -r requirements.txt`
   - Check Python version (3.9+)

4. **Memory Issues**
   - Increase system RAM
   - Reduce concurrent processing
   - Use smaller batch sizes

## 📈 Performance

- **Processing Time**: ~30-60 seconds per application
- **Concurrent Processing**: Up to 10 applications
- **Accuracy**: >95% decision consistency
- **Scalability**: Horizontal scaling supported

## 🔄 Updates

### Version History
- **v2.0.0**: Google Gemini integration
- **v1.5.0**: Multi-agent architecture
- **v1.0.0**: Initial release

### Upcoming Features
- Real-time processing
- Advanced analytics dashboard
- Mobile app integration
- Blockchain verification

---

**Built with ❤️ using CrewAI and Google Gemini**
