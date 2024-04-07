from openai import OpenAI
from pathlib import Path
import json
from dotenv import load_dotenv
from pygame import mixer  # Load the popular external library
#import azure.cognitiveservices.speech as speechsdk

load_dotenv()
client = OpenAI()

def generate_voice(client, texts, voice="alloy"):
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=texts
    )
    
    return response

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
                "description": "Get the piroitity of the airplane in the current ordering given the airplace ID",
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
    ordering.append(airplane_id["airplane_id"])
    print("\n----current ordering----")
    print(ordering)
    print("------------------------\n")

    return json.dumps({"airplane_id": airplane_id, "queue": ordering.index(airplane_id["airplane_id"]) + 1})


def prioritize_airplane(airplane_id):
    """Piroitize the airplane given the airplace ID"""
    if airplane_id in ordering:
        ordering.remove(airplane_id["airplane_id"])
    ordering.insert(0, airplane_id["airplane_id"])
    print("\n----current ordering----")
    print(ordering)
    print("------------------------\n")

    return json.dumps({"airplane_id": "N31469", "priority": "1"})

def get_airplane_priotity(airplane_id):
    """Get the piroitize the airplane given the airplace ID"""
    if airplane_id["airplane_id"] in ordering:
        return json.dumps({"airplane_id": airplane_id["airplane_id"], "priority": ordering.index(airplane_id["airplane_id"]) + 1})
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
    #print(response_message)
    #print(tool_calls)
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

        voice = "shimmer" #"nova" if i%2 ==0 else "alloy"
        response = generate_voice(client, second_response.choices[0].message.content, voice=voice)
        text = second_response.choices[0].message.content
        speech_file_path = Path(__file__).parent / ("reply.mp3")
        response.stream_to_file(speech_file_path)

        mixer.init()
        mixer.music.load(speech_file_path)
        mixer.music.play()
        """

        # Creates an instance of a speech config with specified subscription key and service region.
        speech_key = "6eaea78eb87848b2be4c99bcce78ead7"
        service_region = "eastus"

        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        # Note: the voice setting will not overwrite the voice element in input SSML.
        speech_config.speech_synthesis_voice_name = "zh-CN-liaoning-XiaobeiNeural"

        # use the default speaker as audio output.
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        file_config = speechsdk.audio.AudioOutputConfig(filename="outputaudio.wav")  
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)  

        result = speech_synthesizer.speak_text_async(text).get()
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
        """

        return second_response
#print(run_conversation())
run_conversation("N31469 request to land")
run_conversation("N31480 request to land")
run_conversation("What is the order of N31480?")
run_conversation("28000 request to land, and prioritize 28000")
