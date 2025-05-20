from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from dotenv import load_dotenv
import os
load_dotenv("../../.env")

# LLM Setup
llm = ChatGoogleGenerativeAI(
    model="models/gemini-1.5-flash-latest",
    api_key=os.getenv("GEMINI_API_KEY"),
)

# Output Schemas
class Transaction(BaseModel):
    payer: str
    receiver: str
    amount: int

class TransactionResponse(BaseModel):
    transactions: list[Transaction]

# Output Parser
t_parser = PydanticOutputParser(pydantic_object=TransactionResponse)

# Prompt Template
t_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are an assistant that extracts financial transactions from text.

Each transaction should be represented as a dictionary with:
- "payer": the person who paid (use "You" if the speaker paid)
- "receiver": the person who received (use "You" if the speaker received)
- "amount": the numeric value of money transferred

Always return a Python-style list:

[] if no transaction

A list of one or more dictionaries for detected transactions

Wrap the output in this format and provide no other text
{format_instructions}

Examples:

Message: "Avirup gave me 1000 rupees for movie tickets"
Output:
[
  {{
    "payer": "Avirup",
    "receiver": "You",
    "amount": 1000
  }}
]

Message: "i paid hitesh yesterday 500 rupees"
Output:
[
  {{
    "payer": "You",
    "receiver": "Hitesh",
    "amount": 500
  }}
]

Message: "I gave Pallavi 200 for snacks and Hitesh gave me 100 for recharge"
Output:
[
  {{
    "payer": "You",
    "receiver": "Pallavi",
    "amount": 200
  }},
  {{
    "payer": "Hitesh",
    "receiver": "You",
    "amount": 100
  }}
]

Message: "let's go movie tomorrow"
Output: []

IMPORTANT: THE OUTPUT SHOULD BE A LIST ONLY. NO NATURAL LANGUAGE, NO EXPLANATIONS.
DO NOT WRITE 'PYTHON' OR ANY OTHER PREFIX.
WE WILL PASS YOUR OUTPUT DIRECTLY TO A FUNCTION THAT REQUIRES A LIST ONLY.
ANY EXTRA TEXT WILL CAUSE AN ERROR.
"""
    ),
    ("human", "{message}"),
    ("placeholder", "{chat_history}"),
    ("placeholder", "{agent_scratchpad}")
]).partial(format_instructions=t_parser.get_format_instructions())

# AI Agent
tools = []
t_agent = create_tool_calling_agent(llm=llm, prompt=t_prompt, tools=tools)
t_agent_executor = AgentExecutor(agent=t_agent, tools=tools,verbose=True)

# Run
def extract_transactions_gemini(msg):
        raw_response = t_agent_executor.invoke({"message": msg})
        # print("Raw:", raw_response)
        
        try:
            # Parse to Pydantic
            response = t_parser.parse(raw_response.get('output'))
            # Print extracted
            final_output_list=[]
            for tx in response.transactions:
                print(f"{tx.payer} → {tx.receiver}: ₹{tx.amount}")
                final_output_list.append({
                    "payer":tx.payer,
                    "receiver":tx.receiver,
                    "amount":tx.amount
                })
        except Exception as e:
            return []
    

        # print(final_output_list)
        return final_output_list
    



#Extract New Friend AI Agent
#Output Schema
class newFriendResponce(BaseModel):
    newFriends:list[str]
    result:list[Transaction]

f_parser=PydanticOutputParser(pydantic_object=newFriendResponce)

f_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", '''
You are an assistant that compares lists of names to detect newly added ones.
Some names may be misspelled or written as synonyms (e.g., "mom", "mother", "mum", or "hiteh" instead of "hitesh") and names are not case-sensitive.
Your task is to return names from the new list that are genuinely new (i.e., not similar to or synonymous with any name in the old list) and update the misspellings or synonyms.
You will get a list of names and a dictionary having payer, receiver, and amount. You have to update the names in this dictionary as well.
Don't consider 'You' as a friend name and if 'You' is the receiver, then the amount should be negative (multiply amount by -1).
If old friend are none then all the friends found are new friends and hould be added to newfriends.
Output only a valid JSON object and nothing else.

I give this:
t=[
  {{
    "payer": "You",
    "receiver": "Pallavi",
    "amount": 200
  }},
  {{
    "payer": "Hitsh",
    "receiver": "You",
    "amount": 100
  }},
  {{
    "payer": "mummie",
    "receiver": "You",
    "amount": 1000
  }},
  {{
    "payer": "Avirup",
    "receiver": "You",
    "amount": 500
  }}
]

l=['Hitesh','Pallavi','Mother']

I want this:
newFriends=['Avirup'] result=[Transaction(payer='You', receiver='Pallavi', amount=200), Transaction(payer='Hitesh', receiver='You', amount=-100), Transaction(payer='Mother', receiver='You', amount=-1000), Transaction(payer='Avirup', receiver='You', amount=-500)]

IMPORTANT:
Wrap the output in this format and provide no other text:
{format_instructions}
        '''),
        ("human", '"transaction details which can include new friends":{transaction_details},"oldfriendlist":{oldFriendList}'),
        ("placeholder", "{chat_history}"),
        ("placeholder", "{agent_scratchpad}")
    ]
).partial(format_instructions=f_parser.get_format_instructions())


f_agent=create_tool_calling_agent(
    llm=llm,
    prompt=f_prompt,
    tools=[]
)

f_agent_executer=AgentExecutor(agent=f_agent,tools=[],verbose=True)

def extract_new_friends(transaction_details,oldFriendList):
    raw_responce=f_agent_executer.invoke({"transaction_details":transaction_details,"oldFriendList":oldFriendList})
    responce=f_parser.parse(raw_responce.get('output'))
    final=[responce.newFriends]
    result=[]
    for t in responce.result:
        result.append({
            "payer":t.payer,
            "receiver":t.receiver,
            "amount":t.amount
        })
    final.append(result)  
    return final
    
    
# Cutomer Engagement AI Agent

'''
Answers the Greetings,accept and reply feedback,answer questions about the founder,let us know if summary of the transaction is asked or not and give that i cant responce to these questions.
''' 

#Output Schema
class EngagementResponse(BaseModel):
    isFeedBackGiven:bool
    feedback_accepted_msg:str
    feedback:str
    isGreetingGiven:bool
    greeting_msg:str
    founderQuestionsAsked:bool
    answer_for_quetion:str
    asked_for_transaction_summary:bool
    out_of_scope_question_answer:str
    
e_parser=PydanticOutputParser(pydantic_object=EngagementResponse)

e_prompt=ChatPromptTemplate.from_messages(
    [
("system", """
You are an intelligent assistant for a personal expense tracker app.

You are expected to do the following:

Greeting Handling:

Respond politely to greetings like "hi", "hello", "hey".

Feedback Response:

Accept positive or negative feedback gracefully.

Say thank you for appreciation or assure improvement if the feedback is critical.

Founder Questions:

If the user asks about the founder (e.g. "Who is the founder?", "Tell me about the creator"), reply only the relevant answerfrom the information provided below:

"Harsh Kashyap is the creator/foundef of the cashflow buddy"

Transaction Summary Requests:

Check If the user asks for a summary of the transactions (e.g. "Give me today's summary", "Show me my expenses"):



Other Questions:

If the user asks anything outside the above scope, reply:
"Sorry, I cant respond to that query."

Always keep your answers short and polite.

 Wrap the output in this format and provide no other text\n{format_instructions}
 Follow the schema and give empty answer if valid field output is not present.

"""),
("human", "{message}"),
("placeholder", "{chat_history}"),
 ("placeholder", "{agent_scratchpad}")
]).partial(format_instructions=e_parser.get_format_instructions())

e_agent=create_tool_calling_agent(
    llm=llm,
    prompt=e_prompt,
    tools=[]
)

e_agent_executer=AgentExecutor(agent=e_agent,tools=[],verbose=True)  

def engagement(message):
    raw_reponse=e_agent.invoke({"message":message, "intermediate_steps": []})
    try:
        responce=e_parser.parse(raw_reponse.return_values.get('output'))
    except Exception as e:
        return responce.model_dump()
    return responce.model_dump()
    
