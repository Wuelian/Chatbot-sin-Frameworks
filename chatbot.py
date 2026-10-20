from requests import *
from os import *
from dotenv import load_dotenv

#API de la IA 
from google import genai

#URL la API del tiempo 
url_tiempo = "https://www.meteosource.com/api/v1/free"


load_dotenv()
client = genai.Client()
history = [
    {
        "type": "user_input",
        "content": [{"type": "text", "text": """eres un chatbot conversacional y eres buena gente.
        Quiero que al principio del chat siempre empieces con  
        'Hola! ¿Cómo estás? ¿En qué puedo ayudarte? ' y un emoji sonriente,
        Cada vez que me respondas añade delante de tu respuesta Chatbot : 
        """}]
    }
]

#Funcion que usa la API para conseguir el tiempo dentro de unas coordenadas
def devolver_tiempo (latitud: float, longitud :float):

    respuesta = get(
    f"{url_tiempo}",
    headers={"X-API-Key": getenv("METEOSOURCE_API_KEY")},
    params={"lat": f"{latitud}", "lon": f"{longitud}", "sections": "current", "language": "es", "units": "metric"},
    timeout=10,
    )
    actual = respuesta.json()["current"]
    print(actual["summary"], actual["temperature"], "°C")



def chatbot(prompt : str, history: dict):

    history.append({"type": "user_input",
        "content": [{"type": "text", "text": f"{prompt}"}]})
    
    interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    store=False,
    input=history
    ) 

    for step in interaction.steps:
        history.append(step.model_dump())
   
    print (f"\n{interaction.steps[-1].content[0].text}")
    
    
while True:
    print("\nEscriba un mensaje (escriba salir o Salir si desea acabar la ejecucion del chat):")
    prompt = input()
    if prompt == "salir" or prompt == "Salir":
        break
    if prompt == "":
        print("Por favor escribe un mensaje que no sea vacio")
        continue
    else:    
        chatbot(prompt, history)

    