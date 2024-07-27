import streamlit as st
import speech_recognition as sr
from googlesearch import search
from gtts import gTTS
import os
from dotenv import load_dotenv
from groq import Groq
import smtplib
import pyttsx3

api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    st.error("GROQ_API_KEY environment variable is not set!")
else:
    client = Groq(api_key=api_key)



def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def search_online(query):
    try:
        search_results = list(search(query, num_results=1))
        return search_results[0] if search_results else "No results found."
    except Exception as e:
        print(f"Error during web search: {e}")
        return "An error occurred while searching online."

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"Recognized text: {text}")
            return text
        except sr.UnknownValueError:
            st.write("Could not understand audio")
            return None
        except sr.RequestError:
            st.write("Could not request results; check your network connection")
            return None
        except Exception as e:
            st.write(f"An error occurred during speech recognition: {e}")
            return None

def generate_response(system_message, prompt):
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt + " give response in one line"}
            ],
            temperature=1,
            max_tokens=150,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.write(f"Error generating response: {e}")
        return "Sorry, I couldn't generate a response."

def send_email(to_address, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        msg = 'Subject: {}\n\n{}'.format(subject, body)
        server.starttls()
        server.login('koundinyasaran@gmail.com', 'gugr gdxr qvwy ilkg')
        server.sendmail('koundinyasaran@gmail.com', to_address, msg)
        server.quit()
        st.write("Email sent successfully")
    except Exception as e:
        st.write(f"Failed to send email: {e}")

def book_appointment():
    while True:
        speak_text("Provide your name - you just have to spell your name")
        name = recognize_speech()
        
        if "its" in name.lower() or "my name is" in name.lower() or "it's" in name.lower():
            name = name.lower().replace("its", "").replace("my name is", "").replace("it's",'')
        name = name.replace(" ", "")
        speak_text(name)
        speak_text("Say Yes or No")
        confirm = recognize_speech()
        if "yes" in confirm.lower():
            break
        else:
            speak_text("Let's try again.")

    while True:
        speak_text("Provide your phone number.")
        phone = recognize_speech()
        if not phone:
            continue
        speak_text(phone)
        speak_text("Say Yes or No")
        confirm = recognize_speech()
        if "yes" in confirm.lower():
            break
        else:
            speak_text("Let's try again.")

    while True:
        speak_text("Provide the date for the appointment.")
        date = recognize_speech()
        if not date:
            continue
        speak_text(date)
        speak_text("Say Yes or No")
        confirm = recognize_speech()
        if "yes" in confirm.lower():
            break
        else:
            speak_text("Let's try again.")

    while True:
        speak_text("Provide the time for the appointment.")
        time = recognize_speech()
        if not time:
            continue
        speak_text(time)
        speak_text("Say Yes or No")
        confirm = recognize_speech()
        if "yes" in confirm.lower():
            break
        else:
            speak_text("Let's try again.")

    appointment_details = f"Details: \nName: {name}\nPhone: {phone}\nDate: {date}\nTime: {time}"

    speak_text("Should we send the appointment details to your email?")
    confirm_email = recognize_speech()

    if "yes" in confirm_email.lower():
        while True:
            speak_text("Please provide your email address.")
            email_address = recognize_speech()
            if not email_address:
                continue
            if "at" in email_address.lower() or "at the rate" in email_address.lower():
                email_address = email_address.lower().replace("at the rate", "@").replace("at", "@")
                email_address = email_address.replace(" ", "")

            if "@" in email_address and "." in email_address.split("@")[-1]:
                speak_text(email_address)
                speak_text("Say Yes or No")
                confirm = recognize_speech()
                if "yes" in confirm.lower():
                    send_email(email_address, "Appointment Booking", appointment_details)
                    speak_text("Appointment details have been sent to your email.")
                    break
                else:
                    speak_text("Let's try again.")
    else:
        speak_text("Okay, the appointment is booked without email confirmation.")

def voice_chatbot(system_message):
    initial_greeting = "Hey, I'm Sandy. How can I assist you today?"
    speak_text(initial_greeting)

    while True:
        query = recognize_speech()
        if query:
            if "goodbye" in query.lower() or "thank you" in query.lower() or "bye" in query.lower():
                speak_text("Thank you for calling us. Goodbye!")
                break
            elif "search" in query.lower() or "not sure" in query.lower():
                search_result = search_online(query)
                speak_text(search_result)
            elif "book appointment" in query.lower() or "appointment" in query.lower():
                book_appointment()
                break
            else:
                response = generate_response(system_message, query)
                speak_text(response)

st.title("Voice Chatbot for BMW Car Showroom")
st.write("Interact with the chatbot by clicking the button below.")

system_message = st.text_input("Enter the system message", 
                               "You are Sandy, a helpful BMW car showroom assistant who responds as a known BMW car assistant. All your responses must be one sentence.")

if st.button("Start Chatbot"):
    voice_chatbot(system_message)
