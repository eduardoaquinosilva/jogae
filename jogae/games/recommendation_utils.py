from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Game


def get_content_based_recommendations(user_favorite_games, all_games, num_recommendations=5):
    if not user_favorite_games:
        return []
    
    game_content = []
    for game in all_games:
        genres = ' '.join([genre.name for genre in game.genres.all()])
        tags = ' '.join([tag.name for tag in game.tags.all()])
        content = f"{game.title} {game.description} {genres} {tags}"
        game_content.append(content)
    
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(game_content)

    user_game_indices = [list(all_games).index(game) for game in user_favorite_games]

    user_profile = tfidf_matrix[user_game_indices].mean(axis=0)

    cosine_similarities = cosine_similarity(user_profile, tfidf_matrix)

    similar_indices = cosine_similarities.argsort().flatten()[-num_recommendations-len(user_favorite_games):-1]

    recommended_games = []
    for i in reversed(similar_indices):
        if all_games[i] not in user_favorite_games:
            recommended_games.append(all_games[i])
        if len(recommended_games) == num_recommendations:
            break
    
    return recommended_games
