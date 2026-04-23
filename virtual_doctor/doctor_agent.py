"""Doctor Agent — takes a research question, produces a plan."""
import json
import sys
import os
from utils import load_prompt, call_llm, save_artifact

def load_json(json_name):
    if not os.path.exists(json_name):
        return []
    with open(json_name, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(json_name, entries):
    with open(json_name, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)

def run(research_question):
    system = load_prompt("doctor_prompt.md")
    raw = call_llm(system, research_question)

    # Try to parse JSON from response (strip junk if needed)
    start = raw.find("{")
    end = raw.rfind("}") + 1
    response = json.loads(raw[start:end])

    with open("response.json", "w") as file:
        json.dump(response, file, indent=4)

    print(response)
    return response 

"""Read current response and add it into the paitient conversation profile"""
def process_response(current_response):
    
    name = ""
    current_dt = ""
    patient_response = ""
    doctor_reponse = ""
    notes = ""

    if(current_response["Name"]):
        name = current_response["Name"]
    else:
        print("Not a valid json name")
    if(current_response["DateAndTime"]):
        current_dt = current_response["DateAndTime"]
    else:
        print("Not a valid json DT")
    if(current_response["InputFromUser"]):
        patient_response = current_response["InputFromUser"]
    else:
        print("Not a valid json userInput")
    if(current_response["ResponseToUser"]):
         doctor_response = current_response["ResponseToUser"]
    else:
        print("Not a valid json doc response")
    if(current_response["AddToNotes"]):
         notes = current_response["ResponseToUser"]
    else:
        print("Not a valid json notes")



    #Check if patient File exists else make it

    entries = load_json(f"{name}.json")
    entries.append(current_response)
    save_json(f"{name}.json", entries)

    print(f"\n\n{doctor_response}\n\n")

    return (f"\n\n {patient_response} \n\n {doctor_response}")


        


    

        


if __name__ == "__main__":
    """
    question = sys.argv[1] if len(sys.argv) > 1 else (
        "Hello my name is Steve, I have a cough and constant sneezing, a temperature of 101, and many chills. I got sick recently on a road trip to a lake that I swam in."
    )
    run(question)
    """ 

    question = ""
    shouldExit=False 

    if("/exit" in question):
        shouldExit=True

    Previous_Response_Convo = ""
    while(True):
        question = input("Enter input to robo Doctor: ")
        current_response = run(Previous_Response_Convo + "\n\n InputFromUser: " + question)
        Previous_Response_Convo = process_response(current_response)


