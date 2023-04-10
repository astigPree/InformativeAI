'''
    Before running the program you must first install the needed packages ,
    To install it , run the package_installer.py

    If no ERROR : occur , then you can run it

'''

from kivy.core.window import Window

Window.size = (1000, 700)

from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivymd.uix.slider import MDSlider

from kivy.lang.builder import Builder
from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.animation import Animation
from kivy.clock import mainthread

import threading as th
import backend


# ========= Conversation Container
class Chat(MDBoxLayout) :
    chat: Label = ObjectProperty(None)


class ConversationsContainer(MDGridLayout) :

    @mainthread
    def addChat(self, text: str) :
        widget = Chat()
        widget.chat.text = text
        self.add_widget(widget)
        Animation(opacity=1, duration=1).start(widget)
        self.parent.scroll_to(widget)


# ========= Features Container
class FeaturesContainer(MDGridLayout) :
    pass


# ========= Holder of all Widgets
class MainWidget(BoxLayout) :
    features_scroller: ScrollView = ObjectProperty(None)
    ai_picture: Image = ObjectProperty(None)
    conversations: ConversationsContainer = ObjectProperty(None)
    activity_info: Label = ObjectProperty(None)

    # ----> Logo File
    logo = StringProperty('Files/transparent.png')

    # ----> I.A. Pictures Variables
    emotion_training = [
        'ai pictures/training_1.png', 'ai pictures/training_2.png'
    ]
    emotion_talking = [
        'ai pictures/talking_1.png', 'ai pictures/talking_2.png'
    ]
    emotion_listening = [
        'ai pictures/listening_1.png', 'ai pictures/listening_2.png'
    ]

    emotion = StringProperty(emotion_training[0])

    # ----> Features Variables
    is_scrolling_down = True

    # -----> Activity Variables
    is_traning = BooleanProperty(True)
    is_speaking = BooleanProperty(False)
    is_thinking = BooleanProperty(False)
    stop_program = False
    is_voice_man = BooleanProperty(True)

    current_activity = ''  # A.I. current doing or request result

    def __init__(self, **kwargs) :
        super(MainWidget, self).__init__(**kwargs)
        self.speaker = backend.Speaker()
        self.listener = backend.Recognition()
        self.brain = backend.DecisionMaking()
        self.analyzer = backend.ResultAnalyzer()
        self.new_data_handler = backend.NewDataHandler()

        # ----> The activity that A.I. does when user ask about it
        self.activities = {}

    def on_kv_post(self, base_widget) :
        Clock.schedule_interval(self.scrollTheFeaturesContainer, 10)
        Clock.schedule_once(self.changePictures)
        Clock.schedule_interval(self.animateActivityInfo, 1)
        Clock.schedule_once(self.listenToUser)
        Clock.schedule_interval(self.listener.move_threshold, 5)

    # -----> UI Behavior
    def changePictures(self, interval) :
        delay = 2
        if self.is_traning :
            if self.emotion == self.emotion_training[0] :
                self.emotion = self.emotion_training[1]
            else :
                self.emotion = self.emotion_training[0]
            Clock.schedule_once(self.changePictures, 1 / delay)
            return
        if self.is_speaking :
            if self.emotion not in self.emotion_talking :
                self.emotion = self.emotion_talking[1]
            if self.emotion == self.emotion_talking[0] :
                self.emotion = self.emotion_talking[1]
            else :
                self.emotion = self.emotion_talking[0]
            Clock.schedule_once(self.changePictures, 1 / delay)
        else :
            if self.emotion not in self.emotion_listening :
                self.emotion = self.emotion_listening[1]
            if self.emotion == self.emotion_listening[0] :
                self.emotion = self.emotion_listening[1]
            else :
                self.emotion = self.emotion_listening[0]
            Clock.schedule_once(self.changePictures, 1 / delay)

    def scrollTheFeaturesContainer(self, interval) :
        duration = 8
        if self.is_scrolling_down :
            Animation(scroll_y=0, duration=duration).start(self.features_scroller)
            self.is_scrolling_down = False
        else :
            Animation(scroll_y=1, duration=duration).start(self.features_scroller)
            self.is_scrolling_down = True

    def animateActivityInfo(self, interval) :
        if self.is_traning :
            if 'Traning' not in self.activity_info.text :
                self.activity_info.text = "Traning"
            if self.activity_info.text != 'Traning . . . . . .' :
                self.activity_info.text += ' .'
            else :
                self.activity_info.text = "Traning"
            return

        if self.is_thinking :
            if 'Thinking' not in self.activity_info.text :
                self.activity_info.text = "Thinking"
            if self.activity_info.text != 'Thinking . . . . . .' :
                self.activity_info.text += ' .'
            else :
                self.activity_info.text = "Thinking"
            return

        if self.is_speaking :
            if 'Speaking' not in self.activity_info.text :
                self.activity_info.text = "Speaking"
            if self.activity_info.text != 'Speaking . . . . . .' :
                self.activity_info.text += ' .'
            else :
                self.activity_info.text = "Speaking"
        else :
            if 'Listening' not in self.activity_info.text :
                self.activity_info.text = "Listening"
            if self.activity_info.text != 'Listening . . . . . .' :
                self.activity_info.text += ' .'
            else :
                self.activity_info.text = "Listening"

    def doTalking(self, text: str) :
        # -----> Speaking about input data from user
        self.is_thinking = False
        self.is_speaking = True
        self.speaker.talk(text)
        self.is_speaking = False

    # ------> Functions
    def changeAmbient(self, slider: MDSlider) :
        if not isinstance(slider, int) :
            self.listener.change_threshold(slider.value)
        else :
            self.listener.change_threshold(slider)

    def changeVoice(self) :
        self.is_voice_man = not self.is_voice_man
        if self.is_voice_man :
            self.speaker.changeVoiceToMale()
            print('Change To Man Voice')
        else :
            self.speaker.changeVoiceToFemale()
            print('Change To Woman Voice')

    def listenToUser(self, interval) :
        def func() :

            self.brain.create_ai("Datas\\traning data.json", self.activities)
            self.analyzer.load_data("Datas\\ai answers.json", "Datas\\answer keywords.json")
            self.conversations.addChat(backend.introduction)
            self.is_traning = False
            # self.doTalking(backend.introduction)

            mistaken = False
            past_category = ""
            past_convo = ""

            while not self.stop_program :
                # -----> Listening input data from user
                text = self.listener.listen()
                self.is_thinking = True

                print(f'User Input : {text}')

                if text in self.analyzer.errors :
                    # -----> Displaying the result in UI
                    answer , _ = self.analyzer.answer(text, text)
                    self.conversations.addChat(answer)
                    self.doTalking(answer)

                elif mistaken :
                    # ----> If the past conversation is kinda wrong
                    answer , result = self.analyzer.doubt_is_correct(past_category , text ,past_convo )
                    self.conversations.addChat(answer)
                    self.doTalking(answer)
                    mistaken = False
                    past_convo = ""

                else :
                    # -----> Doing the request from input data from user
                    self.current_activity = self.brain.decide(text)
                    print('Category : ', self.current_activity)
                    answer, doubt = self.analyzer.answer(self.current_activity, text)

                    # -----> Displaying the result in UI
                    self.conversations.addChat(answer)
                    self.doTalking(answer)

                    # -----> Doubting the result
                    if not doubt :
                        mistaken = True
                        past_category = self.current_activity
                        past_convo = text

                print()

        th.Thread(target=func).start()


# ========= Application
class InformativeAI(MDApp) :
    title = 'Informative Artificial Intelligence'

    def build(self) :
        return Builder.load_file('design.kv')


if __name__ == '__main__' :
    LabelBase.register(name='title_bar_font', fn_regular='fonts/extrabold.otf')
    LabelBase.register(name='feature_font', fn_regular='fonts/italic.otf')
    LabelBase.register(name='activity_font', fn_regular='fonts/bolditalic.otf')
    LabelBase.register(name='chat_font', fn_regular='fonts/semibolditalic.otf')

    InformativeAI().run()
