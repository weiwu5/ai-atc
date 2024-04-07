from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


ordering = []

atc_functions = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_runway_status",
                "description": "Get the current status of runways at a given airport",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "runway_id": {
                            "type": "string",
                            "description": "runway id, e.g. 1, 2, 3, etc.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_runway_orders",
                "description": "Get the current ordering of runways at a given airport",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "runway_id": {
                            "type": "string",
                            "description": "runway id, e.g. 1, 2, 3, etc.",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_airplace_distance",
                "description": "Get the current ordering of runways at a given airport",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "airplane_id": {
                            "type": "string",
                            "description": "airplane id, e.g. N31469, etc.",
                        },
                    },
                    "required": ["airplane_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "prioritize_airplane",
                "description": "Piroitize the airplane given the airplace ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "airplane_id": {
                            "type": "string",
                            "description": "airplane id, e.g. N31469, etc.",
                        },
                    },
                    "required": ["airplane_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_airplane_priotity",
                "description": "Get the piroitize the airplane given the airplace ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "airplane_id": {
                            "type": "string",
                            "description": "airplane id, e.g. N31469, etc.",
                        },
                    },
                    "required": ["airplane_id"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "queue_airplane",
                "description": "Queue airplane given the airplace ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "airplane_id": {
                            "type": "string",
                            "description": "airplane id, e.g. N31469, etc.",
                        },
                    },
                    "required": ["airplane_id"],
                },
            },
        }
]
# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

def get_runway_status(runway_id):
    """Get the current status of runways at a given airport"""
    if runway_id == 1:
        return json.dumps({"runway_id": 1, "status": "open"})
    else:
        return json.dumps({"runway_id": runway_id, "status": "unknown"})

def get_runway_orders(runway_id):
    """Get the current ordering of runways at a given airport"""
    if runway_id == 1:
        return json.dumps({"runway_id": 1, "order": ordering})
    else:
        return json.dumps({"runway_id": runway_id, "order": "unknown"})

def get_airplace_distance(airplane_id):
    """Get the current ordering of runways at a given airport"""
    if airplane_id == "N31469":
        return json.dumps({"airplane_id": "N31469", "distance": 100})
    else:
        return json.dumps({"airplane_id": airplane_id, "distance": "unknown"})

def queue_airplane(airplane_id):
    """Queue airplane given the airplace ID"""
    ordering.append(airplane_id)
    print(ordering)

    return json.dumps({"airplane_id": airplane_id, "queue": ordering.index(airplane_id) + 1})


def prioritize_airplane(airplane_id):
    """Piroitize the airplane given the airplace ID"""
    if airplane_id in ordering:
        ordering.remove(airplane_id)
    ordering.insert(0, airplane_id)
    print(ordering)

    return json.dumps({"airplane_id": "N31469", "priority": "1"})

def get_airplane_priotity(airplane_id):
    """Get the piroitize the airplane given the airplace ID"""
    if airplane_id in ordering:
        return json.dumps({"airplane_id": airplane_id, "priority": ordering.index(airplane_id) + 1})
    else:
        return json.dumps({"airplane_id": airplane_id, "priority": "unknown"})


def run_conversation(request="What's the weather like in San Francisco, Tokyo, and Paris?"):
    # Step 1: send the conversation and available functions to the model
    messages = [{"role": "user", "content": request}]
    tools = atc_functions
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    print(response_message)
    print(tool_calls)
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_current_weather": get_current_weather,
            "get_runway_status": get_runway_status,
            "get_runway_orders": get_runway_orders,
            "get_airplace_distance": get_airplace_distance,
            "prioritize_airplane": prioritize_airplane,
            "get_airplane_priotity": get_airplane_priotity,
            "queue_airplane": queue_airplane,
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                function_args
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response
#print(run_conversation())
print(run_conversation("N31469 request to land"))
print(run_conversation("28000 request to land, and prioritize 28000"))
