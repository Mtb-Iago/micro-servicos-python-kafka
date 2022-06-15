from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import random
import faker
import json

PROCESSO = "pagamento"
PROCESSO_DE_SEPARACAO_ESTOQUE = "estoque_de_giftcard"

def iniciar():
    global deslocamento
    deslocamento = 0

    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1)
    )
    cliente.add_topic(PROCESSO)
    cliente.close()

def validar_pagamento(informacoes_do_pedido):
    # simula um gasto de tempo de processamento
    sleep(random.randint(1, 6))

    bandeira_cartao = random.choice(
        ["master", "visa16", "visa13", "visa19", "diners"])
    gerador_de_dados_falsos = faker.Faker()
    cartao = gerador_de_dados_falsos.credit_card_number(card_type=bandeira_cartao)

    valido, mensagem = True, "pagamento autorizado para o pedido através do cartão de crédito: " + cartao
    return valido, mensagem


def executar():
    global deslocamento
    resultado = "ok"

    consumidor_de_estoque = KafkaConsumer(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1),
        auto_offset_reset="earliest",
        consumer_timeout_ms=1000)
    particao = TopicPartition(PROCESSO_DE_SEPARACAO_ESTOQUE, 0)
    consumidor_de_estoque.assign([particao])
    consumidor_de_estoque.seek(particao, deslocamento)

    for pedido_de_separacao in consumidor_de_estoque:
        deslocamento = pedido_de_separacao.offset + 1

        informacoes_do_pedido = pedido_de_separacao.value
        informacoes_do_pedido = json.loads(informacoes_do_pedido)

        valido, mensagem = validar_pagamento(informacoes_do_pedido)
        if valido:
            if valido:
                informacoes_do_pedido["sucesso"] = 1
            else:
                informacoes_do_pedido["sucesso"] = 0
            informacoes_do_pedido["mensagem"] = mensagem

            try:
                produtor = KafkaProducer(
                    bootstrap_servers=["kafka:29092"],
                    api_version=(0, 10, 1)
                )
                produtor.send(topic=PROCESSO, value=json.dumps(
                    informacoes_do_pedido).encode("utf-8"))
            except KafkaError as erro:
                resultado = f"erro: {erro}"


    # registrar em um log de operacoes
    print(resultado)


if __name__ == "__main__":
    iniciar()

    agendador = APScheduler()
    agendador.add_job(id=PROCESSO, func=executar,
                      trigger="interval", seconds=3)
    agendador.start()

    while True:
        sleep(60)
