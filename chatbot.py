from requests import *
from os import *
from dotenv import load_dotenv
import json


#API de la IA 
from google import genai

load_dotenv()
#URL la API del tiempo 
url_tiempo = "https://www.meteosource.com/api/v1/free/point"

#Historial de chat con la IA

client = genai.Client()
history = [
    {
        "type": "user_input",
        "content": [{"type": "text", "text": """eres un chatbot conversacional y eres buena gente.
        Cada vez que me respondas añade delante de tu respuesta ---Chatbot : 
        """}]
    }
]

#Funcion que usa la API para conseguir el tiempo dentro de unas coordenadas
def get_tiempo (latitud: float, longitud :float):

    respuesta = get(
    f"{url_tiempo}",
    headers={"X-API-Key": getenv("METEOSOURCE_API_KEY")},
    params={"lat": f"{latitud}", "lon": f"{longitud}", "sections": "current", "language": "en", "units": "metric"},
    timeout=10,
    )
    actual = respuesta.json()["current"]
    print(actual["summary"], actual["temperature"], "°C")
    return {
        "resumen": actual.get("summary"),
        "temperatura": actual.get("temperature"),
        "unidad": "°C",
    }



def chatbot_response(prompt : str, history: dict):

    history.append({"type": "user_input",
        "content": [{"type": "text", "text": f"{prompt}"}]})
    
    interaction = client.interactions.create(
    model="gemini-3.5-flash-lite",
    store=False,
    input=history,
    ) 

    for step in interaction.steps:
        history.append(step.model_dump())
   
    print (f"\n{interaction.steps[-1].content[0].text}")
    
def chatbot_response_fucntionCalling (prompt : str, history: dict):

    history.append({"type": "user_input",
           "content": [{"type": "text", "text": f"{prompt}"}]})
    
    while True:
        interaction = client.interactions.create(
            model="gemini-3.5-flash-lite",
            store=False,
            input=history,
            tools=[weather_tool],
        )

        function_results = []
        for step in interaction.steps:
            history.append(step.model_dump())
            if step.type == "function_call":
                result = available_functions[step.name](**step.arguments)
                print(f"Called {step.name}({step.arguments}) → {result}")
                fn_result = {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [{"type": "text", "text": json.dumps(result)}],
                }
                function_results.append(fn_result)
                history.append(fn_result)

        if not function_results:
            break


weather_tool = {
    "type": "function",
    "name": "get_tiempo",
    "description": (
        """Devuelve el tiempo actual (resumen y temperatura en °C) de una ubicación 
        a partir de sus coordenadas. Úsala cuando el usuario pregunte por el 
        tiempo que hace ahora en algún lugar.
        Tambien mostraras en la terminal una frase de la siguiente forma 'El tiempo de (ubicacion) es x grados' """
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "latitud": {
                "type": "number",
                "description": (
                    """Latitud en grados decimales. Positiva al Norte, negativa al Sur.
                       Ejemplo para Madrid: 40.4168 """
                    
                ),
            },
            "longitud": {
                "type": "number",
                "description": (
                    """Longitud en grados decimales. Positiva al Este, negativa al Oeste. 
                       Ejemplo para Madrid: -3.7038"""
                ),
            },
        },
        "required": ["latitud", "longitud"],
    },
}

available_functions = {
    "get_tiempo": get_tiempo,
}


while True:
    print("\nEscriba un mensaje (escriba salir o Salir si desea acabar la ejecucion del chat):")
    prompt = input()
    if prompt == "salir" or prompt == "Salir":
        break
    if prompt == "":
        print("Por favor escribe un mensaje que no sea vacio")
        continue
    else:    
        chatbot_response(prompt, history)
