from kafka import KafkaConsumer, TopicPartition
from time import sleep
import json

PROCESSO = "listar_livros"
SUGESTAO_LIVROS = "sugerir_livros"

painel_de_sugestao = KafkaConsumer(
    bootstrap_servers = ["kafka:29092"],
    api_version = (0, 10, 1),

    auto_offset_reset = "earliest",
    consumer_timeout_ms=1000)

# particao = TopicPartition(SUGESTAO_LIVROS, 0)
# painel_de_sugestao.assign([particao])

# painel_de_sugestao.seek_to_beginning(particao)
offset = 0
while True:
    print("Esperando Comando para sugestão de livros disponíveis...")

    particao = TopicPartition(SUGESTAO_LIVROS, 0)
    painel_de_sugestao.assign([particao])
    painel_de_sugestao.poll()
    painel_de_sugestao.seek_to_end()

    #for message in painel_de_sugestao:
        # print(message.timestamp)
        # print(message)
        
    for sugerir_livros_disponiveis in painel_de_sugestao:
        offset = sugerir_livros_disponiveis.offset + 1

        comando_sugestao = sugerir_livros_disponiveis.value
        comando_sugestao = json.loads(comando_sugestao)
        
        if (comando_sugestao == "sugerir"):
            print("[PAINEL 04] - Sugerimos através do painel que escolha livros disponíveis...")

    sleep(0.1)
