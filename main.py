import spacy
from flask import Flask, jsonify

app = Flask(__name__)

nlp = spacy.load('en_core_web_trf')

# TERMINALBA:
# export FLASK_APP=main.py
# export FLASK_ENV=development
# flask run vagy flask run --host=0.0.0.0


@app.route('/')
def index():
    return 'Hello!'

def tagger(word, pos, dep):
    invoc = ["MI6, robot, bot"]
    get = ["get", "bring", "fetch", "grab", "obtain", "give"]
    build = ["build", "construct", "erect", "assemble", "make"]
    greeting = ["hi", "hello", "bye", "greetings", "howdy", "welcome"]
    item = ["oak log", "birch log", "stone", "obsidian", "redstone"]
    generic_item = ["wood", "wool"]
    structure = ["house", "igloo", "building"]
    location = ["next", "front", "behind", "here", "there"]
    quantity = ["5", "6", "five", "six"]
    generic_quantity = ["some", "few"]
    # LOCATIONS!! (next to, in front of, etc)

    if word in invoc and dep == "nsubj": return "invoc"
    if word in get: return "get"
    if word in build and (dep == "xcomp" or dep == "conj" or dep == "ROOT"): return "build"
    if word in greeting: return "greeting"
    if word in item: return "item"
    if word in generic_item: return "gen_item"
    if word in structure and pos == "NOUN": return "structure"
    if word in location: return "location"
    if word in quantity: return "quant"
    if word in generic_quantity: return "gen_quant"


response = {
    "message": "", #
    "command_type": "",
    "item": "",
    "quantity": "",
    "structure": "",
    "location": ""
}


def reset_response():
    response["message"] = ""
    response["command_type"] = ""
    response["item"] = ""
    response["quantity"] = ""
    response["structure"] = ""
    response["location"] = ""




@app.route('/<id>/<command>')
def api(id, command):
    print(id)
    doc = nlp(command)

    tagged_words = []
    i = 0
    for token in doc:
        temp = [token.text, token.pos_, token.dep_, token.head.text,
                tagger(token.lemma_.lower(), token.pos_, token.dep_)]
        tagged_words.append(temp)

    print(tagged_words)

    # for items in tagged_words:


    command_struct = []
    for word in tagged_words:
        if word[4] != None:
            command_struct.append(word)

    temp = []
    for command in command_struct:
        temp.append(command[4])
    print(temp)
    print()

    response_list = []

    for i in range(len(command_struct)):
        if command_struct[i][4] == "build":
            try:
                if command_struct[i + 1][4] == "structure":
                    response["command_type"] = command_struct[i][4]
                    response["structure"] = command_struct[i + 1][0]
                    response["message"] = "I will build a(n) " + command_struct[i + 1][0] + "."
                    try:
                        if command_struct[i + 2][4] == "location":
                            response["location"] = command_struct[i + 2][0]
                            response["message"] = "I will build a(n) " + command_struct[i + 1][0] + " " + command_struct[i + 2][0] + "."
                            response_list.append(response.copy())
                            reset_response()
                            i += 2
                        else:
                            response["location"] = "?"
                            response_list.append(response.copy())
                            reset_response()
                    except:
                        response["location"] = "?"
                        response_list.append(response.copy())
                        reset_response()
                        i += 1
            except:
                pass

        if command_struct[i][4] == "get":
            try:
                if (command_struct[i + 1][4] == "quant" or command_struct[i + 1][4] == "gen_quant") and \
                        (command_struct[i + 2][4] == "item" or command_struct[i + 2][4] == "gen_item"):
                    response["command_type"] = command_struct[i][4]
                    response["quantity"] = command_struct[i + 1][0]
                    response["item"] = command_struct[i + 2][0]
                    response["message"] = "I will get you " + command_struct[i + 1][0] + " " + command_struct[i + 2][0] + "."
                    response_list.append(response.copy())
                    reset_response()
                    i += 2
            except:
                pass

            try:
                if command_struct[i + 1][4] == "item" or command_struct[i + 1][4] == "gen_item":
                    response["command_type"] = command_struct[i][4]
                    response["quantity"] = "?"
                    response["item"] = command_struct[i + 1][0]
                    response["message"] = "I will get you " + command_struct[i + 1][0] + "."
                    response_list.append(response.copy())
                    reset_response()
                    i += 1
            except:
                pass

        if command_struct[i][4] == "greeting":
            response["command_type"] = command_struct[i][4]
            response["message"] = "Hello!"
            response_list.append(response.copy())
            reset_response()
            i += 1

    if not response_list:
        response["command_type"] = "Error"
        response["message"] = "Sorry, I didn't understand that."
        response_list.append(response.copy())
        reset_response()

    print(response_list)
    return jsonify(response_list)
