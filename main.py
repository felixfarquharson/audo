#licenced under mit license
import threading
from diart.sources import MicrophoneAudioSource
from diart.inference import RealTimeInference
from diart.pipelines import OnlineSpeakerDiarization, PipelineConfig
import speech_recognition as sr
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

#start a thread to put live clips of each person at a time in folder
pipeline = OnlineSpeakerDiarization(PipelineConfig())
audio_source = MicrophoneAudioSource(pipeline.sample_rate)
inference = RealTimeInference(".", do_plot=True)

listen = threading.Thread(target=inference, args=(pipeline, audio_source))
listen.setDaemon()
listen.start()


#Recognise the clips into text
r = sr.Recognizer()

def process_clip(filename):
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)
        print(text)
    #todo: add to db


#watch the folder for new clips
patterns = ["*"]
ignore_patterns = None
ignore_directories = False
case_sensitive = True
my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)

def on_created(event):
    process_clip(event.src_path)

my_event_handler.on_created = on_created

path = "."
my_observer = Observer()
my_observer.schedule(my_event_handler, path, recursive=False)

my_observer.start()