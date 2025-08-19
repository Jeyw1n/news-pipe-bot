from prometheus_client import Counter, Histogram

MESSAGES_RECEIVED = Counter('messages_received', 'Количество полученных сообщений')
POSTS_GENERATED = Counter('posts_generated', 'Количество сгенерированных статей')
AI_RESPONSE_TIME = Histogram('ai_response_time', 'Время генерации AI текста')

