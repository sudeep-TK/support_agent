# Support Assistant — AI FAQ & Escalation Agent

## Overview
This project is a Support Assistant AI Agent built for the 48-Hour AI Agent Development Challenge.
It answers user queries using a hybrid approach:
- Direct FAQ matching
- AI fallback (GPT model)
- Escalation detection for technical or complex issues

## Live Demo
https://quj4ppyjf9tdhwl8h2apye.streamlit.app/
## Features
- Load or edit FAQ items  
- Simple keyword-based matching  
- Falls back to LLM when FAQ match is low  
- Automatic escalation detection  
- Clean Streamlit UI  
- Quick test buttons for judges

## Tech Stack
- Streamlit  
- OpenAI GPT API  
- Python

## How to Run Locally
1. Install dependencies:
2. Set your OpenAI API key:
- Windows:
  ```
  setx OPENAI_API_KEY "your_key_here"
  ```
- macOS/Linux:
  ```
  export OPENAI_API_KEY="your_key_here"
  ```
3. Run the app:
   
## Architecture Diagram



## Improvements (Optional)
- Add a vector database for smarter retrieval  
- Add login or user tracking  
- Add automatic ticket creation  
- Add logging for conversation history  

