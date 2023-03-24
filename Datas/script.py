





import os
import json
import random

datas = {"intents" :[]}

not_valid = [ "script.py" , "over all data.json" , "answer.txt"]


def get_all_text(file : str) -> list :
	texts = []
	invalid = ["\n" , "" , "\t" ]
	invalid_letter = ( "," ,"?")
	with open(file , 'r' ) as f :
		for text in f.read().split("\n") :
			if text in invalid :
				continue
				
			cleaned = ""
			for letter in text :
				if letter in invalid_letter :
					continue
				cleaned += letter
				
			texts.append(cleaned.lower())
			
	return texts


for file in os.listdir(os.getcwd()):
	data = {"tag": "",
	    "patterns": [],
	    "responses": []
	  }
	if file not in not_valid :
		data["tag"] = os.path.splitext(file)[0]
		data["patterns"] = get_all_text(file)
		data["responses"] = [os.path.splitext(file)[0]]
		
		datas["intents"].append(data)


highest = []
for key , value in datas.items():
	for v in value :
		highest.append( len(v["patterns"]) )

highest = max(highest)
for key , value in datas.items():
	for v in value :
		if len(v["patterns"]) < highest :
			count = highest - len(v["patterns"]) 
			for _ in range(count) :
				v["patterns"].append(random.choice(v["patterns"]))
	

for key , value in datas.items():
	for v in value :
		if len(v["patterns"]) != highest :
			print(v["tags"])


for key , value in datas.items():
	for v in value :
		if len(v["patterns"]) == highest :
			print(f"{v['tag']} : {len(v['patterns'])}  : {len(v['responses'])} ")
			



with open(not_valid[1] , "w") as jf:
	json.dump(datas , jf , indent=4)



