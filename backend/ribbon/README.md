# Ribbon AI Interview API Client

A Python client library for interacting with the Ribbon AI Interview API. This module provides easy-to-use functions for creating interview flows, starting interviews, and retrieving interview results.

## ⚠️ Important Notes

### API Plan Limitations

The current API key has plan limitations:
- **Interview Flow Limit**: The free/basic plan has a cap on the number of interview flows that can be created
- **Optional Fields**: Some advanced features (logo URLs, webhooks, etc.) may require a higher plan tier
- **Interview Type**: Only "recruitment" and "general" types are supported

### Supported Fields

**Always Supported:**
- `org_name` (required)
- `title` (required) 
- `questions` (required)
- `interview_type` ("general" or "recruitment")

**Advanced Features** (may require higher plan):
- `voice_id`
- `language`
- `company_logo_url`
- `additional_info`
- `is_video_enabled`
- `is_phone_call_enabled`
- `is_doc_upload_enabled`
- `redirect_url`
- `webhook_url`

To enable advanced features, initialize the client with:
```python
client = RibbonClient(enable_advanced_features=True)
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API key in a `.env` file:
```bash
RIBBON_API_KEY=your-api-key-here
```

## Quick Start

### 1. Create an Interview Flow

```python
from ribbon_client import create_simple_interview_flow

# Create a simple interview flow
response = create_simple_interview_flow(
    interview_flow_id="my-first-flow",
    org_name="My Company",
    title="Employee Check-in",
    questions=[
        "How are you feeling today?",
        "What's going well this week?",
        "Any challenges you're facing?"
    ]
)
print(f"Flow created: {response}")
```

### 2. Start an Interview

```python
from ribbon_client import start_interview

# Start an interview
interview = start_interview(
    interview_flow_id="my-first-flow",
    interviewee_email="john@example.com",
    interviewee_first_name="John",
    interviewee_last_name="Doe"
)

print(f"Interview Link: {interview['interview_link']}")
print(f"Interview ID: {interview['interview_id']}")
```

### 3. Check Interview Results

```python
from ribbon_client import RibbonClient

client = RibbonClient()

# Check interview status
status = client.get_interview_status("interview-id-here")
print(f"Status: {status}")

if status == "completed":
    # Get transcript
    transcript = client.get_interview_transcript("interview-id-here")
    print(f"Transcript: {transcript}")
    
    # Get audio URL
    audio_url = client.get_interview_audio_url("interview-id-here")
    print(f"Audio: {audio_url}")
```

## Advanced Usage

### Custom Interview Flow

```python
from ribbon_client import RibbonClient, InterviewFlow

client = RibbonClient()

# Create a detailed interview flow
flow = InterviewFlow(
    interview_flow_id="technical-interview-v1",
    org_name="TechCorp",
    title="Senior Developer Interview",
    questions=[
        "Tell me about your experience with Python.",
        "How do you approach debugging complex issues?",
        "Describe a challenging project you've worked on."
    ],
    voice_id="11labs-Kate",
    language="en-US",
    company_logo_url="https://company.com/logo.png",
    additional_info="Technical screening for senior developer role",
    interview_type="technical",
    is_video_enabled=True,
    is_phone_call_enabled=True,
    is_doc_upload_enabled=True,
    redirect_url="https://company.com/interview-complete",
    webhook_url="https://company.com/api/webhook/interview-done"
)

response = client.create_interview_flows([flow])
```

### Full Interview Management

```python
from ribbon_client import RibbonClient, InterviewConfig

client = RibbonClient()

# Create interview with full configuration
config = InterviewConfig(
    interview_flow_id="technical-interview-v1",
    interviewee_email_address="candidate@email.com",
    interviewee_first_name="Jane",
    interviewee_last_name="Smith"
)

interview = client.create_interview(config)

# Get full interview data
interview_data = client.get_interview(interview['interview_id'])
print(f"Full data: {interview_data}")
```

### Batch Operations

```python
from ribbon_client import RibbonClient, InterviewConfig

client = RibbonClient()

# Create multiple interviews
candidates = [
    ("alice@company.com", "Alice", "Johnson"),
    ("bob@company.com", "Bob", "Wilson"),
    ("carol@company.com", "Carol", "Brown")
]

for email, first, last in candidates:
    config = InterviewConfig(
        interview_flow_id="onboarding-v1",
        interviewee_email_address=email,
        interviewee_first_name=first,
        interviewee_last_name=last
    )
    
    interview = client.create_interview(config)
    print(f"Created interview for {first}: {interview['interview_link']}")
```

## API Reference

### Classes

#### `RibbonClient`
Main client for interacting with the Ribbon AI API.

**Methods:**
- `create_interview_flows(flows: List[InterviewFlow])` - Create interview flows
- `create_interview(config: InterviewConfig)` - Start a new interview
- `get_interview(interview_id: str)` - Get full interview data
- `get_interview_status(interview_id: str)` - Get interview status only
- `get_interview_transcript(interview_id: str)` - Get interview transcript
- `get_interview_audio_url(interview_id: str)` - Get audio recording URL

#### `InterviewFlow`
Data class for interview flow configuration.

**Parameters:**
- `interview_flow_id` (str) - Unique identifier
- `org_name` (str) - Organization name
- `title` (str) - Interview title
- `questions` (List[str]) - List of questions
- `voice_id` (str) - Voice ID (default: "11labs-Kate")
- `language` (str) - Language code (default: "en-US")
- `company_logo_url` (Optional[str]) - Logo URL
- `additional_info` (Optional[str]) - Additional information
- `interview_type` (str) - Interview type (default: "general")
- `is_video_enabled` (bool) - Enable video (default: False)
- `is_phone_call_enabled` (bool) - Enable phone (default: True)
- `is_doc_upload_enabled` (bool) - Enable document upload (default: False)
- `redirect_url` (Optional[str]) - Redirect URL after completion
- `webhook_url` (Optional[str]) - Webhook for completion notification

#### `InterviewConfig`
Data class for interview configuration.

**Parameters:**
- `interview_flow_id` (str) - Flow ID to use
- `interviewee_email_address` (Optional[str]) - Interviewee email
- `interviewee_first_name` (Optional[str]) - First name
- `interviewee_last_name` (Optional[str]) - Last name

### Convenience Functions

#### `create_simple_interview_flow(...)`
Quick way to create a basic interview flow with default settings.

#### `start_interview(...)`
Quick way to start an interview with minimal configuration.

## Examples

The repository includes several example scripts:

- `ribbon_client.py` - Main client library with all functionality
- `test_api.py` - Quick test script to verify API functionality  
- `working_example.py` - **Complete working demonstration** (recommended)
- `example_create_flows.py` - Creating different types of interview flows
- `example_manage_interviews.py` - Managing interviews and retrieving results
- `complete_example.py` - Full workflow example (requires flow creation limits)

### Running Examples

```bash
# Test basic API functionality
python test_api.py

# Run the complete working demonstration (RECOMMENDED)
python working_example.py

# Try creating interview flows (if your plan allows)
python example_create_flows.py

# Try managing interviews
python example_manage_interviews.py
```

## Complete Working Example

The `working_example.py` script demonstrates a full workflow that works with current API limitations:

1. **Discovers existing interview flows** that you can use
2. **Creates multiple interviews** for different participants  
3. **Checks interview status and results** in real-time
4. **Shows how to monitor** interview completion
5. **Displays interview transcripts and audio** when available

This is the best example to run to see the full capabilities of the system.

## Error Handling

The client includes comprehensive error handling:

```python
from ribbon_client import RibbonClient

client = RibbonClient()

try:
    interview = client.create_interview(config)
except requests.RequestException as e:
    if e.response.status_code == 403:
        print("Interview flow doesn't belong to your team")
    elif e.response.status_code == 422:
        print("Interview flow not found")
    else:
        print(f"API error: {e}")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Environment Variables

- `RIBBON_API_KEY` - Your Ribbon AI API key (required)

## Dependencies

- `requests` - HTTP client library
- `python-dotenv` - Environment variable loading

## API Endpoints Used

- `POST /v1/interview-flows` - Create interview flows
- `POST /v1/interviews` - Create interviews  
- `GET /v1/interviews/{interview_id}` - Get interview data

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.
