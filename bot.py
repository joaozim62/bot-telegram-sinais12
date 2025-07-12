import os
import yfinance as yf
import pandas as pd
import ta
import logging
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

# Setup
logging.basicConfig(level=logging.INFO)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)
scheduler = BlockingScheduler()

# Lista de ativos B3
ativos = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBDC4.SA"]

def analisar_ativo(ticker):
    try:
        df = yf.download(ticker, period="10d", interval="1h")
        if df.empty:
            logging.warning(f"Nenhum dado para {ticker}")
            return

        df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
        ultimo = df.iloc[-1]
        rsi = ultimo['rsi']

        if rsi < 30:
            sinal = "🚀 *SINAL DE COMPRA*"
        elif rsi > 70:
            sinal = "🔻 *SINAL DE VENDA*"
        else:
            sinal = None

        if sinal:
            mensagem = f"{sinal} detectado para *{ticker}*
RSI: {rsi:.2f}
⏰ {datetime.now().strftime('%d/%m %H:%M')}"
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem, parse_mode='Markdown')
            logging.info(f"Mensagem enviada: {mensagem}")
        else:
            logging.info(f"Sem sinal para {ticker}")

    except Exception as e:
        logging.error(f"Erro ao analisar {ticker}: {e}")

# Tarefa agendada a cada 30 minutos
@scheduler.scheduled_job('interval', minutes=30)
def analisar_todos():
    logging.info("Iniciando análise dos ativos...")
    for ticker in ativos:
        analisar_ativo(ticker)

if __name__ == "__main__":
    logging.info("Bot iniciado com sucesso!")
    analisar_todos()
    scheduler.start()
