import os
import json
import requests

from dotenv import load_dotenv

from tools import search_books

from memory import load_memory, save_memory

from prompts import SYSTEM_PROMPT


load_dotenv()


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)


MODEL = "openrouter/free"


OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)


#################################
# TOOLS
#################################

TOOLS = [

{
"type":"function",

"function":{

"name":"search_books",

"description":
"Search for books by title, author, or keyword.",

"parameters":{

"type":"object",

"properties":{

"query":{

"type":"string",

"description":
"The search query (e.g. title or author)"

}

},

"required":[

"query"

]

}

}

}

]


#################################
# TOOL MAPPING
#################################

TOOL_FUNCTIONS = {


"search_books":

search_books


}


#################################
# CALL LLM
#################################

def call_llm(messages):


    headers = {


        "Authorization":

        f"Bearer {OPENROUTER_API_KEY}",


        "Content-Type":

        "application/json"

    }


    payload = {


        "model":

        MODEL,


        "messages":

        messages,


        "tools":

        TOOLS

    }


    response = requests.post(

        OPENROUTER_URL,

        headers=headers,

        json=payload

    )


    response.raise_for_status()


    return response.json()


#################################
# RUN TOOL
#################################

def run_tool(tool_call):


    tool_name = (
        tool_call["function"]["name"]
    )


    arguments = json.loads(

        tool_call["function"]["arguments"]

    )


    if tool_name in TOOL_FUNCTIONS:


        result = TOOL_FUNCTIONS[tool_name](**arguments)


        return result


    return "Tool not found"


#################################
# AGENT LOOP
#################################

def agent_loop(user_input):


    memory = load_memory()


    messages = [

        {

        "role":

        "system",


        "content":

        SYSTEM_PROMPT

        }

    ]


    messages.extend(memory)


    messages.append(

        {

        "role":

        "user",


        "content":

        user_input

        }

    )


    memory.append(

        {

        "role":

        "user",


        "content":

        user_input

        }

    )


    while True:

        response = call_llm(messages)


        assistant_message = (

            response["choices"][0]["message"]

        )


        if (

            "tool_calls" in assistant_message

            and assistant_message["tool_calls"]

        ):


            memory.append(assistant_message)
            messages.append(assistant_message)


            for tool_call in assistant_message["tool_calls"]:


                result = run_tool(tool_call)


                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["function"]["name"],
                    "content": str(result)
                }


                memory.append(tool_msg)
                messages.append(tool_msg)


            save_memory(

                memory

            )


        else:


            answer = assistant_message.get(

                "content"

            )


            if answer is None:


                return "Unable to answer."


            memory.append(assistant_message)


            save_memory(

                memory

            )


            return answer


#################################
# MAIN
#################################

if __name__ == "__main__":


    print("==========================")
    print(" Book Search AI Agent ")
    print("==========================")
    print()


    while True:


        user = input(

            "You : "

        )


        if user.lower() == "exit":


            break


        try:


            response = agent_loop(user)


            print(

                "\nAgent:",

                response

            )


        except Exception as e:


            print(

                "Error:",

                e

            )