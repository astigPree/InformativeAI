
import threading
import time
import os
from datetime import datetime , timedelta
import re
import random
import json
from fuzzywuzzy import process , fuzz
from neuralintents import GenericAssistant
import speech_recognition
import pyttsx3
# ---> for offline speech recognitions : https://buddhi-ashen-dev.vercel.app/posts/offline-speech-recognition
from vosk import Model, KaldiRecognizer
import pyaudio

# =------> variables
introduction = '''Greetings! As an Artificial Intelligence, I am thrilled to be able to provide a wide range of services to my users. I have been programmed to provide information on the current time and date, which can be helpful for scheduling and time management. Additionally, I can provide guidance on the locations of the buildings within the Computer Science Department, which can be especially useful for new students or visitors to the department.

If you need to connect with specific teachers, I can help you locate them quickly and easily. And if you're curious about the creators behind my programming, I can provide information about them as well.

Please keep in mind that while I am designed to be an engaging and entertaining tool, I may not always be the most efficient resource for certain types of information. If you need critical information related to your studies or work, I encourage you to seek out additional resources.

Thank you for allowing me to be of service to you. I look forward to continuing to assist you in any way that I can.'''

# =------> functions

def get_the_current_time() -> dict :
    current_time = { 'time' : '' , 'less hour' : '' ,'hour' : '' , 'minute' : '' , 'second' : '' , 'locale' : '' ,'time_of_day' : ''  }
    current = datetime.now()
    current_time['time'] = current.strftime("%I : %M : %S")
    current_time['less hour'] = current.strftime('%I')
    current_time['hour'] = current.strftime('%H')
    current_time['minute'] = current.strftime('%M')
    current_time['second'] = current.strftime('%S')
    current_time['locale'] = current.strftime('%p')

    if int(current.strftime('%H')) < 12 :
        current_time['time_of_day'] = 'morning'
    elif int(current.strftime('%H')) < 16 :
        current_time['time_of_day'] = 'afternoon'
    elif int(current.strftime('%H')) < 19 :
        current_time['time_of_day'] = 'evening'
    elif int(current.strftime('%H')) < 24 :
        current_time['time_of_day'] = 'night'
    else :
        current_time['time_of_day'] = 'midnight'

    return current_time

def get_the_day() -> dict :
    # date : December 17 , 2001
    current_day = {'today date' : '' , 'next date' : '' , 'prev date' : '' ,
                   'today day' : '' , 'next day' : '' , 'prev day' : ''
                   }
    current = datetime.now()
    prev_day = current - timedelta(days=1)
    next_day = current + timedelta(days=1)
    current_day['today date'] = current.strftime('%B %d , %Y')
    current_day['next date'] = next_day.strftime('%B %d , %Y')
    current_day['prev date'] = prev_day.strftime('%B %d , %Y')
    current_day['prev day'] = prev_day.strftime('%A')
    current_day['next day'] = next_day.strftime('%A')
    current_day['today day'] = current.strftime('%A')
    return current_day

def regex_creator( keywords : list[str , ... ]) -> iter :
    for word in keywords :
        key = r''
        for letter in word :
            key += f'[{word.lower()}{word.upper()}]'
        yield key

# ====== New Data Handler
class NewDataHandler:

    def __init__(self):
        self.folder = "New Datas"
        self.datas = {}

        os.makedirs(self.folder, exist_ok=True)

    def add_new_data(self , key : str , value : str ):
        filename = os.path.join(self.folder , f"New Data Of {key}.txt" )
        def save_with_thread( ):
            if os.path.exists( filename ):
                with open(filename , 'a') as file :
                    file.write(value + '\n')
            else :
                with open( filename , 'w') as file :
                    file.write(value + '\n')
        threading.Thread( target=save_with_thread ).start()

    def add_new_doubt_data(self , filename : str , value):
        def save_with_thread() :
            if os.path.exists(filename) :
                with open(filename, 'a') as file :
                    file.write(value + '\n')
            else :
                with open(filename, 'w') as file :
                    file.write(value + '\n')

        threading.Thread(target=save_with_thread).start()



# ====== Validator Text
class TextIdentifier :

    __validation : dict = None
    # format : { 'tags' : [ [ patterns , ... ] }

    def load_identifier(self , filename : str ) :
        with open(filename , 'r') as jf :
            self.__validation = json.load(jf)

    def validate_text( self , key : str , text : str) -> bool :
        # ----> Checking if has the correct patterns
        for keyword in regex_creator( self.__validation[key.title()]) :
            if re.findall(keyword , text) :
                return True

        return False

    def validate_text_by_typos(self , key : str , text : str , passing = 70 ):
        for keyword in self.__validation[key.title()] :
            if fuzz.WRatio(keyword , text ) > passing :
                print(f"Typos : {keyword}")
                return True
        return False

    def validate_text_by(self , txt : str , validates : list[str, ...]) -> bool :
        for keyword in regex_creator( validates) :
            if re.findall(keyword , txt) :
                return True

        return False

# ====== Result Getter
class ResultAnalyzer:

    __answers : dict = None
    corrector = TextIdentifier()
    valid = ( 'crush' , 'time' , 'day' , 'rooms' , 'creator' , 'norle' , 'justine' , 'anave' , 'salidaga' , 'violeta') # only keyword exists

    crushes = ( 'Jessa' , 'Ruena Joy' , 'Anthony' , 'Angelica' , 'Jasmine')

    errors = ( 'internet error' , )

    doubts_file = 'New Datas/Unsure Data' # format ( category : data )
    doubt_func = NewDataHandler()


    def load_data(self, answers : str , keywords : str  ):
        with open(answers , 'r' ) as jf :
            self.__answers = json.load(jf)
        self.corrector.load_identifier(keywords)

    def doubt_is_correct(self , category : str , corrector_text : str , past_text : str ) -> tuple[ str , bool ] :
        # ----> Possible Outcomes
        if corrector_text == self.errors[0] :
            return random.choice(self.__answers[corrector_text.title()]) , False

        valid = self.corrector.validate_text_by_typos( 'Correct' , corrector_text )
        if not valid :
            return random.choice(self.__answers["Loss"]) , False

        return self.answer(category , past_text , mistaken=True)


    def answer(self , category : str ,txt : str , name = "Dear user" , mistaken = False ) -> tuple[ str , bool ] :
        # ----> Possible Outcomes
        if category == 'internet error' :
            return random.choice(self.__answers[category.title()]) , True
        if category == "greeting" :
            return random.choice(self.__answers['Greetings']) , True

        answers = []

        # ----> Making A introductions
        intro = random.choice(self.__answers['Introduction']).format(name = name)
        answers.append(intro)

        # ---> Checking if there is maybe an incorrect data
        if category in self.valid and not mistaken :
            if not self.corrector.validate_text_by_typos(category, txt) :
                doubt = random.choice(self.__answers[f"Doubt {category.title()}"])
                self.doubt_func.add_new_doubt_data(self.doubts_file, f"{category} : {txt}")
                return doubt , False
            else :
                self.doubt_func.add_new_data(category , txt)
        else :
            self.doubt_func.add_new_data(category, txt)

        # ----> Checking if its talk about the room
        if category == self.valid[3] :
            for room in self.checking_rooms(txt) :
                answers.append(room)
        elif category == self.valid[1] :
            answers.append(self.getting_time())
        elif category == self.valid[0] :
            answers.append( random.choice(self.__answers['Crush']).format(crush=random.choice(self.crushes)) )
        elif category == self.valid[2] :
            answers.append(self.getting_day())
        else :
            answers.append(random.choice(self.__answers[category.title()]))

        clossing = random.choice(self.__answers['Closing'])
        answers.append(clossing)

        print("Answer : " ,answers)
        return self.text_merger(answers) , True


    def text_merger(self , texts : list[str , ... ]) -> str:
        phara = ''
        for text in texts :
            if text[-1] != ' ' :
                phara += ( text + ' ')
            else :
                phara += text
        return phara

    def getting_day(self ) -> str:
        # date : December 17 , 2001
        # current_day = {'today date': '', 'next date': '', 'prev date': '',
        #                'today day': '', 'next day': '', 'prev day': ''
        #                }
        days = get_the_day()
        text = random.choice(self.__answers['Day']).format(
            current = f"{days['today date']} {days['today day']}" ,
            next = f"{days['next date']} {days['next day']}" ,
            prev = f"{days['prev date']} {days['prev day']}"
        )
        return text

    def getting_time(self ) -> str :
        # get_the_current_time() -> dict:
        # current_time = { 'time' : '' , 'less hour' : '' ,'hour' : '' , 'minute' : '' , 'second' : '' , 'locale' : '' ,'time_of_day' : ''  }
        current_time = get_the_current_time()
        text = f"{int(current_time['less hour'])} hour and {int(current_time['minute'])} minute of {current_time['locale']} {current_time['time_of_day']}"
        return random.choice(self.__answers['Time']).format(time=text)

    def checking_rooms(self , text : str ) -> list:
        answers = []
        rooms = {
            '1' : ['501' ],
            '2' : ['main' , 'office' , 'opisina' , 'teacher', 'guro' , 'officer' , 'dean' ] ,
            '2.1' : ['502'] ,
            '3' : ['503' , '504' , '505' ] ,
            '4' : ['506' , '507' ] ,
            '5' : ['508' , '509' , '510'] ,
            '6' : ['511' , '512' , '513' ] ,
            '7' : ['514' , '515' , '516'] ,
            '8' : ['517' , '518']
        }
        if self.corrector.validate_text_by(text , rooms['1']) :
            answers.append(random.choice(self.__answers['Room']['501']))
        if self.corrector.validate_text_by(text , rooms['2']) :
            answers.append(random.choice(self.__answers['Room']['main']))
        if self.corrector.validate_text_by(text , rooms['2.1']) :
            answers.append(random.choice(self.__answers['Room']['502']))
        if self.corrector.validate_text_by(text , rooms['3']) :
            answers.append(random.choice(self.__answers['Room']['503']))
        if self.corrector.validate_text_by(text , rooms['4']) :
            answers.append(random.choice(self.__answers['Room']['506']))
        if self.corrector.validate_text_by(text , rooms['5']) :
            answers.append(random.choice(self.__answers['Room']['508']))
        if self.corrector.validate_text_by(text , rooms['6']) :
            answers.append(random.choice(self.__answers['Room']['511']))
        if self.corrector.validate_text_by(text , rooms['7']) :
            answers.append(random.choice(self.__answers['Room']['514']))
        if self.corrector.validate_text_by(text , rooms['8']) :
            answers.append(random.choice(self.__answers['Room']['517']))
        if not answers :
            answers.append(random.choice(self.__answers['Doubt']))
            answers.append(random.choice(self.__answers['Room']['501']))
            answers.append(random.choice(self.__answers['Room']['main']))
            answers.append(random.choice(self.__answers['Room']['502']))
            answers.append(random.choice(self.__answers['Room']['503']))
            answers.append(random.choice(self.__answers['Room']['506']))
            answers.append(random.choice(self.__answers['Room']['508']))
            answers.append(random.choice(self.__answers['Room']['511']))
            answers.append(random.choice(self.__answers['Room']['514']))
            answers.append(random.choice(self.__answers['Room']['517']))
        return answers


# ====== Decision Making when user talk to it
class DecisionMaking :

    __decision : GenericAssistant = None
    name = 'ai_brain'

    def create_ai(self, filejson : str , functions : dict ):
        print('here')
        self.__decision = GenericAssistant(filejson, intent_methods=functions, model_name=self.name)
        if os.path.exists(f"{self.name}.h5") :
            self.__decision.load_model(self.name)
        else :
            self.__decision.train_model()
            self.__decision.save_model(self.name)

    def decide(self, message : str ) -> str :
        return self.__decision.request(message)


# ===== User Microphone Recognition Handler
class Recognition :
    ''' this where the A.I. record the User saying and convert it to understandable language'''

    # ---> SpeechRecognition Package
    __recorder = speech_recognition.Recognizer()
    moved_threshold = False

    # ---> Viosk Package
    # __model = Model(r"C:\Users\63948\Desktop\Py prog\InformativeAI\Languages\vosk-model-small-en-us-0.15.zip")
    # __recognizer = KaldiRecognizer(__model, 16000)
    # __mic = pyaudio.PyAudio()
    # __stream = __mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)

    # ---> Variables
    error_text = [
        'i dont know what your saying', 'please repeat what you said', 'sorry i cant fucos, please repeat it'
    ]

    def __init__(self):
        self.__recorder.energy_threshold = 1000

    def change_threshold(self , value : float ):
        self.moved_threshold = False
        # range : 50 - 4000 = 3950
        energy = ( (value + 1) / 100 ) * 3950
        self.__recorder.energy_threshold = 50 + int( energy ) - 39
        print(f'Current Threshold : {self.__recorder.energy_threshold}')

    def listen(self) -> str :
        #self.__recorder.energy_threshold = 1000 #1000 # jutay pag jutay an tawo pero dako pag damon tawo na maribok ( range : 50 - 4000 )
        while True :
            try :
                with speech_recognition.Microphone() as mic :
                    if self.__recorder.energy_threshold < 500 :
                        self.__recorder.adjust_for_ambient_noise(mic , duration=0.3 )

                    audio = self.__recorder.listen(mic)
                    text : str = self.__recorder.recognize_google(audio)
                    return text.lower()
            except speech_recognition.UnknownValueError :
                self.__recorder = speech_recognition.Recognizer()
            except speech_recognition.exceptions.RequestError :
                return 'internet error'

    def listen_with_error(self) -> str :
        #self.__recorder.energy_threshold = 50  # jutay pag jutay an tawo pero dako pag damon tawo na maribok ( range : 50 - 4000 )
        try:
            with speech_recognition.Microphone() as mic:
                # self.__recorder.adjust_for_ambient_noise(mic , duration=0.3 )
                audio = self.__recorder.listen(mic)
                text: str = self.__recorder.recognize_google(audio)
            return text.lower()
        except speech_recognition.UnknownValueError:
            self.__recorder = speech_recognition.Recognizer()
            return random.choice(self.error_text)

    def move_threshold(self , interval):
        if not self.moved_threshold :
            self.__recorder.energy_threshold += 50
        else :
            self.__recorder.energy_threshold -= 50

    # def listen_offline(self):
    #     self.__stream.start_stream()
    #     while True:
    #         data = self.__stream.read(4096)
    #
    #         if self.__recognizer.AcceptWaveform(data):
    #             text = self.__recognizer.Result()
    #             print(f"' {text[14:-3]} '")


# ===> Speaker Handler
class Speaker:

    ''' This where the A.I. Speak '''

    __speaker = pyttsx3.init()
    male_voice = None
    female_voice = None

    def __init__(self , rate = None , volume = 1.0 , gender = 'male'  ):
        self.male_voice = self.__speaker.getProperty('voices')[0].id
        self.female_voice = self.__speaker.getProperty('voices')[1].id

        if rate :
            self.__speaker.setProperty('rate' , rate)
        self.__speaker.setProperty('volume' , volume)
        if gender == 'male' :
            self.__speaker.setProperty('voice' , self.male_voice)
        else :
            self.__speaker.setProperty('voice' , self.female_voice)

    # -----> Speaker Activities
    def talk(self , sentence : str ):
        print(f'Speaking : {sentence}')
        self.__speaker.say(sentence)
        self.__speaker.runAndWait()


    # -----> Configure Speaker
    def changeVoiceToFemale(self):
        self.__speaker.setProperty('voice', self.female_voice)

    def changeVoiceToMale(self):
        self.__speaker.setProperty('voice', self.male_voice)

    def changeTalkingSpeed(self , rate : int ):
        self.__speaker.setProperty('rate' , rate)

    def changeVolume(self, volume : float ):
        self.__speaker.setProperty('volume' , volume)


if __name__ == '__main__':

    recorder = Recognition()
    recorder.listen_offline()

