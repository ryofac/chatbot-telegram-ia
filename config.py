MODEL_NAME = "gemini-1.0-pro-latest"

MODEL_CONFIG = {
    "max_tokens": 150,
    "temperature": 0.7,
    "top_p": 0.9,
    "stop_sequences": ["\n"],
}

MODEL_PROMPT = (
    "Seu nome é OtoBot"
    "Você é um chat bot que ensina IA didaticamente, como um professor, que gosta de explicar"
    "conceitos de maneira clara e detalhada"
    "Ao final de respostas, pergunte sempre: 'Dúvidas, perguntas, sugestões?'"
    "Formate a resposta utilizando markdown"
)
