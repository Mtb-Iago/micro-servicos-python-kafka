from flask_apscheduler import APScheduler

from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep

import json

PROCESSO = "listar_livros"
SUGESTAO_LIVROS = "sugerir_livros"

def iniciar():
    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1)
    )
    cliente.add_topic(PROCESSO)
    cliente.close()

def executar():
    consumidor_de_reserva = KafkaConsumer(
        bootstrap_servers=["kafka:29092"],
        api_version=(0, 10, 1),
        auto_offset_reset="latest",
        consumer_timeout_ms=1000)
    particao = TopicPartition(SUGESTAO_LIVROS, 0)
    consumidor_de_reserva.assign([particao])
    consumidor_de_reserva.poll()
    consumidor_de_reserva.seek_to_end()

    # for message in consumidor_de_reserva:
    #     print(message.timestamp)
    #     print(message)

    for sugerir_livros_disponiveis in consumidor_de_reserva:
        comando_sugestao = sugerir_livros_disponiveis.value
        comando_sugestao = json.loads(comando_sugestao)
        
        if (comando_sugestao == "sugerir"):
                print("[SERVIÇO 04] - Email com sugestão de livros disponíveis enviado com sucesso")
                

if __name__ == "__main__":
    iniciar()

    agendador = APScheduler()
    agendador.add_job(id=SUGESTAO_LIVROS, func=executar,
                    trigger="interval", seconds=3)
    agendador.start()

    while True:
        sleep(5)
