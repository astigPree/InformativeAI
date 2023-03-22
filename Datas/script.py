





import os
import json

datas = {"intents" :[]}

not_valid = [ "script.py" , "over all data.json" , "answer.txt"]


def get_all_text(file : str) -> list :
	texts = []
	invalid = ["\n" , "" , "\t"]
	with open(file , 'r' ) as f :
		for text in f.read().split("\n") :
			if text in invalid :
				continue
			texts.append(text.lower())
	return texts


for file in os.listdir(os.getcwd()):
	data = {"tag": "",
	    "patterns": [],
	    "responses": [],
	    "context_set": ""
	  }
	if file not in not_valid :
		data["tag"] = os.path.splitext(file)[0]
		data["patterns"] = get_all_text(file)
		data["responses"] = [os.path.splitext(file)[0]]
		
		datas["intents"].append(data)
		print(file)
	

with open(not_valid[1] , "w") as jf:
	json.dump(datas , jf , indent=4)



