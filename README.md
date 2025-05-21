# AI Emotional Companion with Tools Support

This project implements an emotional companion assistant using Amazon Bedrock's Nova Sonic model with support for tools functionality.

## Features

- Real-time voice conversation with an emotional companion assistant
- Support for both male (Matthew) and female (Tiffany) voices
- Tool integration for enhanced capabilities:
  - Date and time information
  - Order tracking
  - Weather information
  - Mood-based activity suggestions
- Web interface for easy interaction

## Setup

1. Clone the repository
2. Create a `.env` file with your AWS credentials:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password
SESSION_ENABLE=true
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Run the application:
```
python main.py
```

5. Access the web interface at http://localhost:8100

## Tools Functionality

The assistant can use the following tools:

1. **Date and Time Tool**: Provides current date and time information
2. **Order Tracking Tool**: Simulates tracking an order by ID
3. **Weather Tool**: Provides simulated weather information for a location
4. **Mood Suggestion Tool**: Offers personalized suggestions based on emotional state

## Usage

1. Log in with the credentials from your `.env` file
2. Start speaking with the assistant
3. The assistant will automatically use tools when appropriate based on your conversation
4. Tool results will be displayed in the interface

## Requirements

- Python 3.8+
- AWS account with access to Amazon Bedrock
- Microphone and speakers for voice interaction
