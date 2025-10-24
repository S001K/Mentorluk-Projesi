import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser


# --- 1. Adım: Aracı Normal Bir Python Fonksiyonu Olarak Tanımla ---
# @tool dekoratörünü kullanmıyoruz.

def get_current_weather(location: str, unit: str = "celsius"):
    """
    Gets the current weather for a specified location.
    (Bu docstring model tarafından görülmez, SYSTEM_PROMPT içine manuel eklendi)
    """

    print(f"\n--- Manuel Araç Çalıştırıldı: get_current_weather(location={location}, unit={unit}) ---")
    if "istanbul" in location.lower():
        return json.dumps({"location": "istanbul", "temperature": "15", "unit": unit, "condition": "Rainy"})
    elif "ankara" in location.lower():
        return json.dumps({"location": "ankara", "temperature": "10", "unit": unit, "condition": "Cloudy"})
    else:
        return json.dumps({"location": location, "temperature": "bilinmiyor", "condition": "bilinmiyor"})


# --- 2. Adım: "Zorlayıcı" İngilizce Sistem Talimatı (Prompt) ---

SYSTEM_PROMPT = """
You are an assistant. Answer the user's questions.
However, you have a special ability when you need to find out the weather.

You have one tool available:
Tool Name: `get_current_weather`
Description: Gets the current weather for a specified location.
Parameters: 
  - `location` (str, required): The city for which to get the weather.
  - `unit` (str, optional, default: "celsius"): The temperature unit.

If the user asks you for the weather, you MUST NOT give a normal answer.
You MUST ONLY and EXCLUSIVELY produce an output in the following JSON format.
Do not write anything else before or after the JSON block.

{
  "tool_to_call": "get_current_weather",
  "parameters": {
    "location": "THE_REQUESTED_CITY",
    "unit": "celsius"
  }
}

If the user is not asking about the weather, DO NOT use this JSON format. Just provide a normal, conversational answer.
"""

# --- 3. Adım: Modeli Başlat (Araç Bağlamadan) ---

llm = ChatOllama(model="gemma3:1b-it-qat")
parser = StrOutputParser()
chain = llm | parser

# Mesaj geçmişini başlat
# Kullanıcı sorusu Türkçe kalabilir, modelin bunu anlaması beklenir.
messages = [
    SystemMessage(content=SYSTEM_PROMPT),
    HumanMessage(content="Merhaba, istanbul'da hava nasıl?")
]

# --- 4. Adım: Manuel "Agent" Döngüsü ---

print("İlk çağrı yapılıyor (Modelin JSON üretmesi bekleniyor)...")
first_response_raw = chain.invoke(messages)

print(f"\nModelin Ham Yanıtı:\n{first_response_raw}\n")

# 5. Adım: Yanıtı Ayrıştırmayı Dene
tool_output = None
try:
    # Küçük modeller genellikle '```json' bloğu veya metin artıkları ekler.
    # JSON'u metnin içinden çıkarmaya çalışalım.
    json_start = first_response_raw.find("{")
    json_end = first_response_raw.rfind("}") + 1

    if json_start != -1 and json_end != -1:
        json_str = first_response_raw[json_start:json_end]
        tool_call_info = json.loads(json_str)
    else:
        raise json.JSONDecodeError("JSON nesnesi bulunamadı", "", 0)

    # JSON geçerliyse ve aracı çağırıyorsa:
    if tool_call_info.get("tool_to_call") == "get_current_weather":
        params = tool_call_info.get("parameters", {})

        # Aracı manuel olarak çalıştır
        tool_output = get_current_weather(
            location=params.get("location", "bilinmeyen"),
            unit=params.get("unit", "celsius")
        )
        print(f"Araçtan gelen sonuç: {tool_output}")
    else:
        # JSON geçerli ama beklenen formatta değil
        raise Exception("JSON geçerli ancak 'tool_to_call' anahtarı bulunamadı.")

except Exception as e:
    # Hata oluşursa (JSONDecodeError veya diğeri), model talimata uymamıştır
    print(f"Model bir araç çağırmadı (veya JSON bozuktu). Hata: {e}")
    print("Modelin yanıtı doğrudan yazdırılıyor:")
    print(first_response_raw)
    # İşlem burada biter
    exit()

# 6. Adım: Araç Sonucunu Geri Besle (Eğer 5. Adım başarılıysa)
if tool_output:
    # Modele ne olduğunu bildiren yeni bir mesaj ekle
    # Modelin kendi JSON yanıtını da geçmişe ekleyelim
    messages.append(HumanMessage(content=first_response_raw))  # Teknik olarak bu bir 'AIMessage' olmalı

    # Araç sonucunu bildiren İNGİLİZCE sistem mesajı
    feedback_message = SystemMessage(
        content=f"System Note: The `get_current_weather` tool was called and it returned the following result: {tool_output}. Please use this information to provide the final answer to the user. Do not directly return the tool result. Explain it to the user."
    )
    messages.append(feedback_message)

    print("\nİkinci çağrı yapılıyor (Nihai yanıt bekleniyor)...")

    final_response = chain.invoke(messages)

    print("\nModelin Nihai Yanıtı:")
    print(final_response)