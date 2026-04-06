# ─────────────────────────────────────────────────────────────────────────────
# test_claude.py  –  Send an invoice to Claude and get an AP decision
# ─────────────────────────────────────────────────────────────────────────────

# Step 1: Import the libraries we need.
# - 'os' lets us read environment variables (like our API key).
# - 'dotenv' loads the .env file so Python can see those variables.
# - 'anthropic' is the official library for talking to Claude.
import os
from dotenv import load_dotenv
import anthropic

# Step 2: Load the .env file.
# This reads the file called ".env" in the same folder and makes every
# line (e.g. ANTHROPIC_API_KEY=sk-ant-...) available as an environment variable.
load_dotenv()

# Step 3: Read the API key from the environment.
# os.getenv("ANTHROPIC_API_KEY") looks up the variable we just loaded.
api_key = os.getenv("ANTHROPIC_API_KEY")

# Step 4: Safety check – tell the user clearly if the key is missing.
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found. Make sure your .env file exists and contains the key.")

# Step 5: Create the Anthropic client.
# We pass our key so the library knows how to authenticate every request.
client = anthropic.Anthropic(api_key=api_key)

# Step 6: Write the invoice text that we want Claude to evaluate.
# Triple-quoted strings (""" ... """) let us write multi-line text easily.
invoice = """
Vendor: Wipro
Amount: ₹2,45,000
GL Code: 620200
Status: on-hold
"""

# Step 7: Build the prompt we will send to Claude.
# We combine the invoice details with the question we want answered.
user_message = f"""Here is the invoice:
{invoice}
You are an AP processor. Given this invoice, should I Approve, Escalate, or Return to Vendor? Give a one-line reason."""

# Step 8: Send the message to Claude and wait for the response.
# - model        : which Claude model to use (Opus 4.6 is the most capable)
# - max_tokens   : the maximum length of Claude's reply (1024 is plenty here)
# - messages     : the conversation — here it's just one message from the user
print("Sending invoice to Claude...\n")

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": user_message}
    ]
)

# Step 9: Extract the text from the response.
# response.content is a list of content blocks; we grab the first text block.
reply = response.content[0].text

# Step 10: Print the result so the user can read it.
print("Claude's decision:")
print(reply)
