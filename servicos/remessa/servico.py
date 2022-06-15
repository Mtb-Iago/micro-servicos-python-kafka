from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import random
import json

import smtplib
from email.message import EmailMessage
from password import *

PROCESSO = "remessa_de_giftcard"
PROCESSO_DE_PAGAMENTO = "pagamento"

def iniciar():
    global deslocamento
    deslocamento = 0

    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1)
    )
    cliente.add_topic(PROCESSO)
    cliente.close()


EMAIL = "***@gmail.com"
MAIL_SERVER = "smtp.gmail.com"
PORT = 465


def enviar_email_para_desbloqueio(cliente, informacoes_de_pagamento):
    sucesso, mensagem = True, "desbloqueio solicitado via email"

    email = EmailMessage()
    email.set_content("Prezado(a), " + cliente["nome"] +
                      ",\n\nPara liberar o seu giftcard, clique no link abaixo:\n\n" +
                      "http://localhost:5002/executar/" + informacoes_de_pagamento["identificacao"])
    email["Subject"] = "Desbloqueie o seu GiftCard"
    email["From"] = EMAIL
    email["To"] = cliente["e_mail"]

    try:
        server = smtplib.SMTP_SSL(MAIL_SERVER, PORT)

        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, cliente["e_mail"], email.as_string())

        server.quit()
    except Exception as erro:
        sucesso, mensagem = False, "não foi possível enviar o e-mail, erro: " + str(erro)
        # print(e)

    return sucesso, mensagem


BANCO_DADOS_DE_ENVIO = "/workdir/dados_de_envio.json"
def validar_remessa(informacoes_de_pagamento):
    # simula um gasto de tempo de processamento
    sleep(random.randint(1, 6))

    valida, mensagem = False, "remessa não autorizada"

    with open(BANCO_DADOS_DE_ENVIO, "r") as arquivo_dados_de_envio:
        dados_de_envio = json.load(arquivo_dados_de_envio)
        clientes = dados_de_envio["clientes"]

        mensagem = "dados de envio não encontrados"
        for cliente in clientes:
            if cliente["id"] == informacoes_de_pagamento["id_cliente"]:
                valida, mensagem = enviar_email_para_desbloqueio(
                    cliente, informacoes_de_pagamento)

                break

    return valida, mensagem


def executar():
    global deslocamento
    resultado = "ok"

    consumidor_de_pagamentos = KafkaConsumer(
        bootstrap_servers=["kafka:29092"],
        auto_offset_reset='earliest',
        consumer_timeout_ms=1000,
        api_version=(0, 10, 1))
    particao = TopicPartition(PROCESSO_DE_PAGAMENTO, 0)
    consumidor_de_pagamentos.assign([particao])
    consumidor_de_pagamentos.seek(particao, deslocamento)

    for pagamento in consumidor_de_pagamentos:
        deslocamento = pagamento.offset + 1

        informacoes_do_pagamento = pagamento.value
        informacoes_do_pagamento = json.loads(informacoes_do_pagamento)

        valida, mensagem = validar_remessa(informacoes_do_pagamento)
        if valida:
            informacoes_do_pagamento["sucesso"] = 1
        else:
            informacoes_do_pagamento["sucesso"] = 0
        informacoes_do_pagamento["mensagem"] = mensagem

        try:
            produtor = KafkaProducer(
                bootstrap_servers=["kafka:29092"],
                api_version=(0, 10, 1)
            )
            produtor.send(topic=PROCESSO, value=json.dumps(
                informacoes_do_pagamento
            ).encode("utf-8"))
        except KafkaError as erro:
            resultado = f"erro: {erro}"

    # deveria enviar para um log
    print(resultado)


if __name__ == "__main__":
    iniciar()

    agendador = APScheduler()
    agendador.add_job(id=PROCESSO, func=executar,
                      trigger="interval", seconds=3)
    agendador.start()

    while True:
        sleep(60)
