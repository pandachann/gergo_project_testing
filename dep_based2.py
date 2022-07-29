import spacy

import warnings
warnings.filterwarnings("ignore")

nlp = spacy.load('en_core_web_trf')

# GLOBAL VARIABLES

state = "default"

gen_response = {
    "root": "",
    "det": "",
    "attr": "",
    "obj": ""
}

response = {
    "message": "",
    "command_type": "",
    "item": "",
    "quantity": "",
    "structure": "",
    "location": ""
}

# Logs unknown or not specific parameters of the response
unknown_params = {
    "command_type": "",
    "item": "",
    "quantity": "",
    "structure": "",
    "location": ""
}

commands_dict = {
    "get": ["get", "bring", "fetch", "grab", "obtain", "give", "want"],
    "build": ["build", "construct", "erect", "assemble"],
    "move": ["move", "go"],
    "dance": ["dance", "jam"],
    "craft": ["craft", "make", "create"],
    "heard": ["heard"]
}

items_dict = {
    "gen_item": ["wood", "oak", "wool"],
    "spec_item": ["cobblestone", "oak log", "golden hoe", "dirt"]
}

quant_dict = {
    "gen_quant": ["some", "few", "lot", "much", "many"],
    "spec_quant": ["5", "6", "five", "six"]
}


# HELPER METHODS

def reset_gen_response():
    gen_response["root"] = ""
    gen_response["det"] = ""
    gen_response["attr"] = ""
    gen_response["obj"] = ""


def reset_response():
    response["message"] = ""
    response["command_type"] = ""
    response["item"] = ""
    response["quantity"] = ""
    response["structure"] = ""
    response["location"] = ""


# MAIN METHODS

def preproc(query):
    print(query)
    global doc
    doc = nlp(query)
    if state == "default":
        proc()
        gen2spec()
    else:
        ask_proc()


def proc():
    reset_gen_response()

    for sent in doc.sents:
        # PATTERN 4
        if len(list(sent.root.children)) == 1 and list(sent.root.children)[0].dep_ == "advmod":
            gen_response["root"] = sent.root.lemma_
            gen_response["obj"] = list(sent.root.children)[0].lemma_

        else:
            for child in sent.root.children:

                # PATTERN 1
                if child.dep_ == "dobj":
                    gen_response["root"] = sent.root.lemma_
                    gen_response["obj"] = child.lemma_

                    for child2 in child.children:
                        if child2.dep_ == "det" or child2.dep_ == "nummod":
                            gen_response["det"] = child2.lemma_
                        if child2.dep_ == "amod" or child2.dep_ == "compound":
                            gen_response["attr"] = child2.lemma_

                # PATTERN 3
                if child.dep_ == "prep":
                    for child2 in child.children:
                        if child2.dep_ == "pobj":
                            gen_response["root"] = sent.root.lemma_
                            gen_response["obj"] = child2.lemma_

                            for child3 in child2.children:
                                if child3.dep_ == "amod" or child3.dep_ == "compound":
                                    gen_response["attr"] = child3.lemma_

                if child.dep_ == "xcomp":
                    gen_response["root"] = sent.root.lemma_

                # PATTERN 2
                if child.dep_ == "nsubj":
                    gen_response["obj"] = child.lemma_

                    for child2 in child.children:
                        if child2.dep_ == "det" or child2.dep_ == "nummod":
                            gen_response["det"] = child2.lemma_
                        if child2.dep_ == "amod" or child2.dep_ == "compound":
                            gen_response["attr"] = child2.lemma_

    print("proc:")
    print(gen_response)
    return


def gen2spec():
    global state

    greeting = ["hi", "hello", "bye", "greetings", "howdy", "welcome"]
    item = ["oak log", "birch log", "stone", "obsidian", "redstone"]
    generic_item = ["wood", "wool"]
    structure = ["house", "igloo", "building"]
    location = ["next", "front", "behind", "here", "there"]

    search_comm_dict = {l: k for k, v in commands_dict.items() for l in v}
    search_item_dict = {l: k for k, v in items_dict.items() for l in v}
    search_quant_dict = {l: k for k, v in quant_dict.items() for l in v}

    if search_comm_dict[gen_response["root"]] == "get":
        response["command_type"] = search_comm_dict[gen_response["root"]]

        # Get name of the item from gen_response (e.g: if attr = "oak" and obj = "log" -> item="oak log";
        # if attr = "" and obj = "cobblestone" -> item = "cobblestone")
        if gen_response["attr"]:
            response["item"] = gen_response["attr"] + " " + gen_response["obj"]
        else:
            response["item"] = gen_response["obj"]

        if gen_response["det"]:
            response["quantity"] = gen_response["det"]

        # Decide if given item is specific or not
        # (e.g: specific = cobblestone, oak log, etc, non-specific (generic) = wood, wool, etc)
        if search_item_dict[response["item"]] == "gen_item":
            state = "ask"
            unknown_params["item"] = "??"

        if search_quant_dict[response["quantity"]] == "gen_quant" or response["quantity"] == "":
            state = "ask"
            unknown_params["quantity"] = "??"

    print("gen2spec:")
    print(response)
    print(unknown_params)


def ask_proc():
    if unknown_params["item"] == "??":
        print("Missing item!")


# TEST

# state = "ask"

preproc("get some wood please")
