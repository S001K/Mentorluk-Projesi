from langchain_ollama.chat_models import ChatOllama
from langchain_core.messages import BaseMessage
from config import LLM_MODEL


class OllamaClient:
    """
    Singleton wrapper for the Ollama ChatModel (e.g., gemma3:1b).
    All agents import and reuse this instance.
    """

    _instance = None

    def __new__(cls, model_name: str = LLM_MODEL, base_url: str = "http://localhost:11434"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.chat_model = ChatOllama(model=model_name, base_url=base_url)
        return cls._instance

    def get_chat_model(self):
        return self.chat_model

    def generate_response(self, messages: list[BaseMessage]):
        """
        Generates a response from the chat model.

        messages: list of LangChain BaseMessage objects (HumanMessage, AIMessage, etc.)
        returns: AIMessage object from LLM
        """

        response_message = self.chat_model.invoke(messages)

        return response_message.content


# Example Usage
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage, AIMessage

    client = OllamaClient()

    # Create a sample history
    message_history = [
        HumanMessage(content="Hello, my name is Sinan."),
        AIMessage(content="Hello Sinan! How can I help you today?")
    ]

    # Add a new question
    message_history.append(HumanMessage(content="What is my name?"))

    # Generate the response
    response = client.generate_response(message_history)
    print(f"AI: {response}")