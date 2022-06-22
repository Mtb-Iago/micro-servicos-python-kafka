from kafka import KafkaConsumer, TopicPartition
from time import sleep
import json

REQUISICAO = "requisicao"

painel_de_sugestao = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

while True:
    particao = TopicPartition(REQUISICAO, 0)
    painel_de_sugestao.assign([particao])
    painel_de_sugestao.poll()
    painel_de_sugestao.seek_to_end()
        
    for sugerir_livros_disponiveis in painel_de_sugestao:
        comando_sugestao = sugerir_livros_disponiveis.value
        comando_sugestao = json.loads(comando_sugestao)

        print("[PAINEL 02] - requisição recebida ID Nº: ", comando_sugestao)

    sleep(0.3)