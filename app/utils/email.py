import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def enviar_correo(destinatario: str, asunto: str, mensaje: str):
    remitente = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    # Comprobación básica
    if not remitente or not password:
        print("⚠️ Falta configurar EMAIL_SENDER o EMAIL_PASSWORD en el archivo .env")
        return

    # Crear el mensaje MIME
    msg = MIMEMultipart()
    msg["From"] = remitente
    msg["To"] = destinatario
    msg["Subject"] = asunto

    msg.attach(MIMEText(mensaje, "plain"))

    try:
        # Conectarse al servidor SMTP de Gmail
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        servidor.send_message(msg)
        servidor.quit()
        print("✅ Correo enviado con éxito.")
    except Exception as e:
        print("❌ Error al enviar correo:", e)
