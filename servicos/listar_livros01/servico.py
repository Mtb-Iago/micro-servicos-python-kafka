#SERVICO 01 - LISTAR LIVROS 
from flask_apscheduler import APScheduler
from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep
import json

PROCESSO = "listar_livros"

def iniciar():
    global deslocamento
    deslocamento = 0

    cliente = KafkaClient(
        bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
    cliente.add_topic(PROCESSO)
    cliente.close()


BANCO_ACERVO_LIVROS = "/workdir/acervo.json"
def listar_livros_acervo():
    
    with open(BANCO_ACERVO_LIVROS, "r") as livros_acervo:
        acervo = json.load(livros_acervo)
        livros = acervo["livros_acervo_biblioteca"]
            
        livros_acervo.close()
    try:
        produtor = KafkaProducer(
            bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
        produtor.send(topic=PROCESSO, value=json.dumps(
            livros).encode("utf-8"))
        # print(livros)
    except KafkaError as erro:
        resultado = f"erro: {erro}"
    
    return print(f"Lista de livros guardada")

if __name__ == "__main__":
    iniciar()

    agendador = APScheduler()
    agendador.add_job(id=PROCESSO, func=listar_livros_acervo,
                    trigger="interval", seconds=3)
    agendador.start()

    while True:
        sleep(60)
