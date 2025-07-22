import pickle
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from games.models import Game, GameTFIDF

class Command(BaseCommand):
    help = 'Pré-Computa a matriz TF-IDF para recomendação de conteúdo.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando a pré-computação de TF-IDF...'))

        # Use prefetch_related para carregar os gêneros e tags de forma eficiente
        all_games = list(Game.objects.all().prefetch_related('genres', 'tags'))
        if not all_games:
            self.stdout.write(self.style.WARNING('Não foi encontrado jogos na base de dados. Encerrando...'))
            return

        self.stdout.write(f'Localizado {len(all_games)} jogos. Gerando conteúdo...')

        # Coleta informações de gênero, tags, descrição e título do jogo e junta tudo, guardando em um vetor
        game_content = []
        for game in all_games:
            genres = ' '.join([genre.name for genre in game.genres.all()])
            tags = ' '.join([tag.name for tag in game.tags.all()])
            content = f"{game.title} {game.description} {genres} {tags}"
            game_content.append(content)


        # Ignorando palavras 'inúteis' para o processamento de linguagem natural e retirando palavras muito incomuns e as muito comuns
        self.stdout.write('Calculando a matriz TF-IDF...')
        tfidf = TfidfVectorizer(
            stop_words='english',
            min_df=3, 
            max_df=0.85, 
        )
        tfidf_matrix = tfidf.fit_transform(game_content)

        # Usando a representação do UUID em string para ser compatível com JSON
        # game.id - > chave do dicionario, representando o jogo
        # i -> valor do dicionário, representando a linha na matriz TFIDF
        self.stdout.write('Criando o mapa de índices de jogos...')
        game_index_map = {str(game.id): i for i, game in enumerate(all_games)}

        # Serializa a matriz usando pickle para ser possível armazenar na base de dados
        pickled_matrix = pickle.dumps(tfidf_matrix)

        # Limpa os dados antigos e salva a pré computação nova
        self.stdout.write('Salvando a nova matriz TF-IDF na base de dados...')
        GameTFIDF.objects.all().delete()
        GameTFIDF.objects.create(
            tfidf_matrix=pickled_matrix,
            game_index_map=game_index_map,
        )

        self.stdout.write(self.style.SUCCESS('Sucesso na operação de pré-computação e armazenamento da matriz TF-IDF!'))
        