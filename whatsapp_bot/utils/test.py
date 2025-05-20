import google.generativeai as genai
import json

# Set your Gemini API key
genai.configure(api_key="")

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
        print('RAW',raw)
        start = raw.find('[')
        end = raw.rfind(']')
        raw_list_str = raw[start:end+1] if start != -1 and end != -1 else "[]"
        print('JSON',json.loads(raw_list_str))
        return json.loads(raw_list_str)
    
    except Exception as e:
        print(str(e))
        return [{"error": str(e), "raw_output": raw}]


if __name__=="__main__":
    message='''
    Yesterday I went to the restaurant with my gf I bought her a great wine for 500 rupees 
    and then we went shopping with  my gf and 
    she bought me a great t-shirt worth 5000!!
    '''
    extract_transactions_gemini(message)