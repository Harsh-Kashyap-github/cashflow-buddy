import google.generativeai as genai
import json

# Set your Gemini API key
# genai.configure(api_key="")

model = genai.GenerativeModel('models/gemini-1.5-flash-latest')

def extract_transactions_gemini(message):
    prompt = f"""
You are an assistant that extracts financial transactions from text.

Each transaction should be represented as a dictionary with:
- "payer": the person who paid (use "You" if the speaker paid)
- "reciever": the person who received (use "You" if the speaker received)
- "Amount": the numeric value of money transferred

**Always return a Python-style list:**
- [] if no transaction
- A list of one or more dictionaries for detected transactions

Examples:

Message: "Avirup gave me 1000 rupees for movie tickets"
Output:
[
  {{
    "payer": "Avirup",
    "reciever": "You",
    "Amount": 1000
  }}
]

Message: "i paid hitesh yesterday 500 rupees"
Output:
[
  {{
    "payer": "You",
    "reciever": "Hitesh",
    "Amount": 500
  }}
]

Message: "I gave Pallavi 200 for snacks and Hitesh gave me 100 for recharge"
Output:
[
  {{
    "payer": "You",
    "reciever": "Pallavi",
    "Amount": 200
  }},
  {{
    "payer": "Hitesh",
    "reciever": "You",
    "Amount": 100
  }}
]

Message: "let's go movie tomorrow"
Output: []

Now process this message:
"{message}"
Output:

NOTE:THE OUTPUT SHOULD BE A LIST ONLY NO NATURAL LANGUAGE
.DONT WRITE PYTHON OR ANY OTHER LETTER JUST LIST AND INFO INSIDE IT.
WE WILL PASS YOUR OUTPUT DIRECTLY TO OUR FUCNTION WHICH TAKES LIST AS INPUT SO IF YOU GIVE ANY OTHER VALUE WITH IT WE WILL GET ERROR.
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Try to parse Python-style list as JSON
        raw = raw.replace("'", '"') # Convert single to double quotes
        # ('RAW',raw)
        start = raw.find('[')
        end = raw.rfind(']')
        raw_list_str = raw[start:end+1] if start != -1 and end != -1 else "[]"
        print('JSON',json.loads(raw_list_str))
        return json.loads(raw_list_str)
    
    except Exception as e:
        print(str(e))
        return [{"error": str(e), "raw_output": raw}]
      

def detect_new_friends(listOfFriends, oldFriends):
    """
    Detects new friends by comparing the current list with the old one using LLM.
    Handles misspellings and synonyms like 'mom', 'mother', etc.
    """
    prompt = f"""
Given two lists of names:

Old Friends List:
{json.dumps(oldFriends)}

New List of Friends:
{json.dumps(listOfFriends)}

Some names may be misspelled or written as synonyms (e.g., "mom", "mother", "mum", or "hiteh" instead of "hitesh").
Return a JSON list of names from the new list that are genuinely new (not similar or synonyms of names in the old list).
Output only the list of new friends.
"""

    response = model.generate_content(prompt)
    
    try:
        # Try parsing the response into a list
        new_friends = json.loads(response.text)
        if isinstance(new_friends, list):
            return new_friends
        else:
            return []
    except json.JSONDecodeError:
        # Fallback: extract names manually from response
        lines = response.text.strip().splitlines()
        possible_names = [line.strip('- ').strip() for line in lines if line.strip()]
        return possible_names
      
# if __name__=='__main__':
#   l=['alex','mom','mother','hitesh']
#   old=['mum','hitesh']
  
#   print(detect_new_friends(l,old))