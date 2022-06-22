# AVALIAÇÃO 2 DDI

### Sobre o projeto:
    1 - é realmente necessário startar o container iniciar_bd_estatico primeiro,
    para que haja o carregamento do banco de dados no Kafka.

    2 - Após o start do container iniciar_bd_estatico aconselho verificar se todos os containers estão startados
    (Houve um caso em que um zookeeper não rodou de primeira e após atualizar o status fui perceber que estava parado.)

    3 - O container iniciar_bd_estatico vai apenas rodar o script 1 uma vez via docker-compose e vai parar (é normal)
    ele é o único que vai ficar "stop" da lista de containers

    4 - O processo a partir daí segue seu fluxo normal.
    
    5 - Endpoint para envio de id dos livros de [1...5] 
        http://localhost:5002/escolherLivro/{id}

    -   Agradecimentos ao Prof Luiz por nos apresentar essa ferramenta tão incrivel.

                                                      Iago Oliveira.
