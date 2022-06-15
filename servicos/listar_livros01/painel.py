from kafka import KafkaConsumer, TopicPartition
from time import sleep
import json

PROCESSO = "listar_livros"

painel_de_acervo = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

particao = TopicPartition(PROCESSO, 0)
painel_de_acervo.assign([particao])

painel_de_acervo.seek_to_beginning(particao)
offset = 0
while True:
    print("esperando pedidos de separacao...")

    for pedido in painel_de_acervo:
        dados_do_pedido = json.loads(pedido.value)
    print("dados do pedido: ", dados_do_pedido)
    sleep(5)

# painel_de_estoque.close()