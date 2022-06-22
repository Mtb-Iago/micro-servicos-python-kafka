from flask_apscheduler import APScheduler
from kafka import KafkaClient, KafkaProducer, KafkaConsumer, TopicPartition
from kafka.errors import KafkaError

from time import sleep

import json

PROCESSO = "listar_livros"
CONFIRMACAO_RESERVA = "confirmar_reserva"

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
        auto_offset_reset="earliest",
        consumer_timeout_ms=1000)
    particao = TopicPartition(CONFIRMACAO_RESERVA, 0)
    consumidor_de_reserva.assign([particao])
    consumidor_de_reserva.poll()
    consumidor_de_reserva.seek_to_end()

    for pedido_de_separacao in consumidor_de_reserva:
        
        informacoes_do_pedido = pedido_de_separacao.value
        informacoes_do_pedido = json.loads(informacoes_do_pedido)
        print(informacoes_do_pedido)
        
        lista_atualizada = buscar_lista_livro(informacoes_do_pedido)
        try:
            produtor = KafkaProducer(
                bootstrap_servers=["kafka:29092"], api_version=(0, 10, 1))
            produtor.send(topic=PROCESSO, value=json.dumps(
                lista_atualizada).encode("utf-8"))
            # print(livros)
        except KafkaError as erro:
            resultado = f"erro: {erro}"
        return print(lista_atualizada)

def buscar_lista_livro(informacao_reserva):
    PROCESSO = "listar_livros"

    painel_de_acervo = KafkaConsumer(
        bootstrap_servers = ["kafka:29092"],
        api_version = (0, 10, 1),
        auto_offset_reset = "earliest",
        consumer_timeout_ms=1000)

    particao = TopicPartition(PROCESSO, 0)
    painel_de_acervo.assign([particao])
    painel_de_acervo.seek_to_beginning(particao)
    
    for pedido in painel_de_acervo:
        dados_do_pedido = json.loads(pedido.value)
    
    index = 0
    for _ in dados_do_pedido:
        if dados_do_pedido[index]['id'] == informacao_reserva:
            dados_do_pedido[index]['disponibilidade'] = False
        index += 1
    
    painel_de_acervo.close()
    return dados_do_pedido

if __name__ == "__main__":
    iniciar()
    
    agendador = APScheduler()
    agendador.add_job(id=PROCESSO, func=executar,
                        trigger="interval", seconds=3)
    agendador.start()

    while True:
        sleep(0.3)
