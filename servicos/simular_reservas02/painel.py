from kafka import KafkaConsumer, TopicPartition
from time import sleep
import json

painel_de_desbloqueios = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

particao = TopicPartition("listar_livros", 0)
painel_de_desbloqueios.assign([particao])

painel_de_desbloqueios.seek_to_beginning(particao)
offset = 0
while True:
    print("Simulando reserva...")

    for desbloqueio in painel_de_desbloqueios:
        offset = desbloqueio.offset + 1

        dados_do_desbloqueio = json.loads(desbloqueio.value)
        print("Listagem do acervo: ", dados_do_desbloqueio)

    painel_de_desbloqueios.seek(particao, offset)

    sleep(5)