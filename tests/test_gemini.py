#!/usr/bin/env python3
"""
Simple test to check if Google Generative AI is working
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
print(f"GOOGLE_API_KEY is set: {bool(GOOGLE_API_KEY)}")

if GOOGLE_API_KEY:
    try:
        import google.generativeai as genai
        print("Successfully imported google.generativeai")
        
        # Configure the API
        genai.configure(api_key=GOOGLE_API_KEY)
        print("Successfully configured API key")
        
        # Try to create a model
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("Successfully created model")
        
        # Try a simple prompt
        response = model.generate_content("Say hello in one word")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Error with Google Generative AI: {e}")
        import traceback
        traceback.print_exc()
else:
    print("GOOGLE_API_KEY not found in environment")