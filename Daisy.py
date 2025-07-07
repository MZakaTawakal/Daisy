import speech_recognition as sr
import pyttsx3
import requests
import json
from datetime import datetime
import time

class DaisyAssistant:
    def __init__(self):
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # API Keys
        self.weather_api_key = "e6e68666588fd2aeea419d8fc6a59455"
        self.deepseek_api_key = "sk-734c810bb5374821a24da17f7d6189a6"
        
        # Adjust for ambient noise on startup
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Daisy: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self, timeout=5, phrase_time_limit=10):
        """Listen for voice input and convert to text"""
        with self.microphone as source:
            try:
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                # Convert to text using Google's speech recognition
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                self.speak(f"Speech recognition error: {e}")
                return None
    
    def get_weather(self, city="Bandar Lampung"):
        """Fetch weather information"""
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
        
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if response.status_code == 200:
                temp = round(data['main']['temp'])
                feels_like = round(data['main']['feels_like'])
                description = data['weather'][0]['description']
                humidity = data['main']['humidity']
                
                return (f"The weather in {city} is {temp} degrees Celsius, "
                       f"feels like {feels_like} degrees, with {description}. "
                       f"Humidity is {humidity} percent.")
            else:
                return f"I couldn't find weather information for {city}"
                
        except Exception as e:
            return "Sorry, I couldn't fetch the weather information right now."
    
    def ask_deepseek(self, query):
        """Get AI-powered responses using DeepSeek API"""
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant. Give brief, clear answers."},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 150
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return "I'm having trouble connecting to my knowledge base."
                
        except Exception as e:
            return "Sorry, I couldn't process that request right now."
    
    def process_command(self, command):
        """Process user commands and return appropriate response"""
        if not command:
            return "I didn't catch that. Could you please repeat?"
        
        # Basic commands
        if any(word in command for word in ["hello", "hi", "hey"]):
            return "Hello Master! How can I assist you today?"
        
        elif "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        elif "date" in command:
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"Today's date is {current_date}"
        
        # Weather command
        elif "weather" in command:
            # Extract city name if mentioned
            if " in " in command:
                city = command.split(" in ")[-1].strip()
            else:
                city = "Bandar Lampung"  # Default city
            
            return self.get_weather(city)
        
        # AI-powered search/questions
        elif any(phrase in command for phrase in ["what is", "who is", "tell me about", "search", "how to"]):
            # Clean up the query
            for phrase in ["search for", "what is", "who is", "tell me about", "how to"]:
                command = command.replace(phrase, "").strip()
            
            self.speak("Let me think about that...")
            return self.ask_deepseek(command)
        
        # Exit commands
        elif any(word in command for word in ["goodbye", "bye", "exit", "quit", "stop"]):
            return "GOODBYE"
        
        # Default: use AI for general queries
        else:
            self.speak("Let me help you with that...")
            return self.ask_deepseek(command)
    
    def run(self):
        """Main loop for the assistant"""
        self.speak("Hello! I'm Daisy, your assistant. Say 'Hey Daisy' to wake me up.")
        
        wake_words = ["hey daisy", "hi daisy", "hello daisy", "daisy"]
        
        while True:
            try:
                # Listen for wake word
                print("\nListening for wake word...")
                wake_input = self.listen(timeout=None, phrase_time_limit=3)
                
                if wake_input and any(wake in wake_input for wake in wake_words):
                    self.speak("Yes master, how may I help?")
                    
                    # Listen for command
                    command = self.listen(timeout=5, phrase_time_limit=10)
                    
                    if command is not None:
                        # Process the command
                        response = self.process_command(command)
                        
                        if response == "GOODBYE":
                            self.speak("Goodbye Master! Have a great day!")
                            break
                        else:
                            self.speak(response)
                    else:
                        self.speak("I didn't hear anything. Say 'Hey Daisy' when you need me.")
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                self.speak("I encountered an error. Let me reset.")
                time.sleep(2)
        
        self.speak("Assistant shutting down. Goodbye!")

# Run the assistant
if __name__ == "__main__":
    assistant = DaisyAssistant()
    assistant.run()