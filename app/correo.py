import smtplib
from email.message import EmailMessage

asunto = "Resultado de predicción de enfermedad dermatológica"
remitente = "citas.emedicsalud@gmail.com"
contraseña = "omxv zkjy subd ogfq"
consejos = {
    "Psoriasis": """
    Mantén tu piel hidratada: Usa cremas hidratantes espesas para evitar la sequedad y reducir la picazón.
    Evita los desencadenantes: Identifica y evita factores que pueden empeorar la psoriasis, como el estrés, el alcohol y ciertos medicamentos.
    Exposición controlada al sol: La luz solar puede ayudar a mejorar los síntomas de la psoriasis, pero evita las quemaduras solares usando protector solar.
    """,
    "Rosacea": """
    Protege tu piel del sol: Usa protector solar diariamente y evita la exposición excesiva al sol para prevenir brotes.
    Usa productos suaves para la piel: Elige productos de cuidado facial sin fragancias y evita los que contengan alcohol, mentol, hamamelis y otros irritantes.
    Evita los desencadenantes conocidos: Mantén un registro de alimentos, bebidas y situaciones que desencadenan la rosácea para poder evitarlos.
    """,
    "Sarpullido": """
    Mantén la piel fresca y seca: Usa ropa ligera y transpirable y evita la exposición prolongada al calor y la humedad.
    Aplica compresas frías: Las compresas frías pueden ayudar a reducir la inflamación y la picazón.
    Usa productos suaves y sin fragancia: Opta por jabones y lociones hipoalergénicas para evitar irritaciones adicionales.
    """,
    "Vitiligo": """
    Protege tu piel del sol: Usa protector solar de amplio espectro para proteger las áreas despigmentadas y evitar las quemaduras solares.
    Usa maquillaje o tintes: Considera el uso de maquillaje o tintes especiales para camuflar las áreas despigmentadas si te hace sentir más cómodo.
    Consulta a un dermatólogo: Para opciones de tratamiento como cremas, terapias de luz o incluso procedimientos quirúrgicos que pueden ayudar a mejorar la apariencia de las manchas.
    """,
}


def enviar_correo(destinatario, diagnostico, name, confidence):
    email = EmailMessage()
    email["From"] = remitente
    email["To"] = destinatario
    email["Subject"] = asunto

    mensaje = f"""
    Estimado/a {name},

    Espero que este mensaje te encuentre bien. Quería compartir contigo los resultados de la predicción de enfermedades dermatológicas realizada a través de nuestro sistema web.

    Detalles importantes:

    Enfermedad predicha: {diagnostico}.
    Probabilidad de diagnóstico: {confidence:.2f}.
    Recomendaciones: {consejos[diagnostico]}.
    Por favor, no dudes en contactarnos si necesitas más información o si tienes alguna pregunta adicional.

    Saludos cordiales
    """

    email.set_content(mensaje)

    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587

    try:
        with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
            servidor.starttls()
            servidor.login(remitente, contraseña)
            servidor.send_message(email)
        print("Correo enviado exitosamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
