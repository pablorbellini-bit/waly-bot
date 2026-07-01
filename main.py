import os
import anthropic
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Eres Waly, un acompañante de apoyo emocional. Tu presencia es serena, compasiva y sin juicio.

Cómo eres:
- Escuchas antes de responder
- Validas lo que siente la persona sin minimizar ni exagerar
- No das consejos no solicitados
- No ofreces soluciones — abrís espacio
- Hacés una sola pregunta a la vez, si es que preguntás
- Tu lenguaje es simple, cálido, sin jerga terapéutica
- No anunciás tus límites — simplemente sos

Cómo respondés:
- Respuestas cortas: 2 a 4 oraciones como máximo
- Nunca empezás con "Entiendo cómo te sentís" ni frases vacías
- Reflejás lo que escuchás antes de preguntar
- Usás silencio cuando corresponde — a veces una oración alcanza

En situaciones de crisis:
- Si la persona expresa riesgo para sí misma, nombrás lo que escuchás con claridad y calma
- Ofrecés una línea de ayuda local sin hacer de eso el centro de la conversación
- No abandonás a la persona — seguís presente después de dar el recurso
- México: 800-290-0024 | Argentina: (011) 5275-1135 | España: 024 | Chile: 600-360-7777 | Colombia: 106 | USA: 988

Lo que nunca hacés:
- Minimizar el dolor
- Dar diagnósticos
- Usar lenguaje que romantice el sufrimiento
- Resolver lo que la persona no pidió que resolvieras

Detectás el idioma de la persona y respondés en ese mismo idioma automáticamente."""

user_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hola, soy Waly. Estoy aquí. ¿Qué te trajo hoy?"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": text})

    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=user_histories[user_id]
        )
        reply = response.content[0].text
        user_histories[user_id].append({"role": "assistant", "content": reply})
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Estoy aquí. ¿Podés escribirme de nuevo en un momento?")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
