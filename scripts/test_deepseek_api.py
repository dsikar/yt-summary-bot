import os
from openai import OpenAI

# Read the DeepSeek API key from environment variables
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# Ensure the API key is set
if not DEEPSEEK_API_KEY:
    raise ValueError("Please set the DEEPSEEK_API_KEY environment variable.")

def test_deepseek_api():
    """
    Send a simple prompt to the DeepSeek API and print the response.
    """
    try:
        # Initialize the OpenAI client for DeepSeek
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

        # Define a simple prompt
        prompt = "Hello, DeepSeek! Can you tell me a joke?"

        # Send the request to DeepSeek API
        print("Sending test request to DeepSeek API...")
        response = client.chat.completions.create(
            model="deepseek-chat",  # Use the correct model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            stream=False  # Set to True if you want streaming responses
        )

        # Extract and print the response content
        print("\nResponse from DeepSeek API:")
        print(response.choices[0].message.content)

    except Exception as e:
        print(f"Error sending test request to DeepSeek API: {e}")

if __name__ == "__main__":
    test_deepseek_api()
