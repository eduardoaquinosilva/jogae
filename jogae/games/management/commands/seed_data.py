import random
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files import File
from django.contrib.auth import get_user_model
from games.models import Game, Genre, Tag
from app_profile.models import Friendship
from app_biblioteca.models import FavoriteGamesByUser

User = get_user_model()

# Define game archetypes to create coherent data for recommendations.
GAME_THEMES = [
    {
        'theme': 'Fantasy RPG',
        'titles': ["Dragon's Fall", "The Elden Scroll", "Sorcerer's Quest", "Kingdom of Ash"],
        'description_template': 'An epic open-world fantasy RPG where you must {action} to save the realm.',
        'actions': ['slay ancient dragons', 'uncover a lost prophecy', 'master forbidden magic'],
        'genres': ['RPG', 'Adventure'],
        'tags': ['Fantasy', 'Open World', 'Singleplayer', 'Magic'],
        'image_folder': 'fantasy'
    },
    {
        'theme': 'Sci-Fi Shooter',
        'titles': ['Galaxy at War', 'Starship Trooper', 'Cybernetic Dawn', 'Void Runner'],
        'description_template': 'A fast-paced multiplayer shooter set in a distant future. You must {action}.',
        'actions': ['command a powerful mech', 'fight for galactic supremacy', 'survive against alien hordes'],
        'genres': ['Action', 'Shooter'],
        'tags': ['Sci-Fi', 'Multiplayer', 'Co-op', 'First-Person'],
        'image_folder': 'scifi'
    },
    {
        'theme': 'Historical Strategy',
        'titles': ['Empire Divided', 'Medieval Tactics', 'Rise of the Khanate', 'Feudal Lords'],
        'description_template': 'A grand strategy game where you {action} to build a lasting dynasty.',
        'actions': ['lead massive armies in historical battles', 'manage the economy of your kingdom', 'engage in complex diplomacy'],
        'genres': ['Strategy', 'Simulation'],
        'tags': ['Historical', 'Turn-Based', 'Singleplayer', 'Grand Strategy'],
        'image_folder': 'strategy'
    },
]

def get_image_files(image_folder):
    image_dir = os.path.join(settings.BASE_DIR, 'seed_images', image_folder)
    if os.path.isdir(image_dir):
        return [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]
    return []

class Command(BaseCommand):
    help = 'Seeds the database with sample data for users, games, and friendships.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Deleting old data...")
        # Clear existing data to avoid duplicates on re-runs
        User.objects.filter(is_superuser=False).delete()
        Game.objects.all().delete()
        Genre.objects.all().delete()
        Tag.objects.all().delete()
        Friendship.objects.all().delete()
        FavoriteGamesByUser.objects.all().delete()

        self.stdout.write("Creating new data...")

        # === Create Users ===
        self.stdout.write("Creating users...")
        users = []
        for i in range(10):
            username = f'user{i+1}'
            user = User.objects.create_user(username=username, password='password123')
            users.append(user)
            self.stdout.write(f"  Created user: {username}")

        # === Create Genres and Tags ===
        self.stdout.write("Creating genres and tags...")
        all_genre_names = set(g for theme in GAME_THEMES for g in theme['genres'])
        all_tag_names = set(t for theme in GAME_THEMES for t in theme['tags'])

        genres_db = {name: Genre.objects.create(name=name) for name in all_genre_names}
        tags_db = {name: Tag.objects.create(name=name) for name in all_tag_names}

        # === Create Games ===
        self.stdout.write("Creating games...")
        games = []
        game_titles = set()

        for i in range(30): # Create 30 games
            theme = random.choice(GAME_THEMES)
            
            # Ensure unique titles
            title = random.choice(theme['titles'])
            while title in game_titles:
                title = f"{random.choice(theme['titles'])} {i+2}"
            game_titles.add(title)

            description = theme['description_template'].format(action=random.choice(theme['actions']))

            game = Game.objects.create(
                title=title,
                description=description,
                user=users[i % len(users)],
                rating=round(random.uniform(3.0, 5.0), 1),
            )

            # Attach a theme-appropriate image
            image_files = get_image_files(theme['image_folder'])
            if image_files:
                image_name = random.choice(image_files)
                image_path = os.path.join(settings.BASE_DIR, 'seed_images', theme['image_folder'], image_name)
                with open(image_path, 'rb') as f:
                    game.picture.save(image_name, File(f), save=True)

            # Add genres and tags from the theme
            game.genres.set([genres_db[name] for name in theme['genres']])
            game.tags.set([tags_db[name] for name in theme['tags']])
            
            # Store the theme with the game for later use
            game.theme_name = theme['theme']
            games.append(game)
            self.stdout.write(f"  Created game: {game.title}")

        # === Create Friendships ===
        self.stdout.write("Creating friendships...")
        for user in users:
            num_friends = random.randint(2, 3)
            potential_friends = [u for u in users if u != user]
            friends_to_add = random.sample(potential_friends, k=min(num_friends, len(potential_friends)))

            for friend in friends_to_add:
                # Avoid creating duplicate friendships
                if not Friendship.objects.filter(
                    from_user=user, to_user=friend
                ).exists() and not Friendship.objects.filter(
                    from_user=friend, to_user=user
                ).exists():
                    Friendship.objects.create(
                        from_user=user,
                        to_user=friend,
                        status=Friendship.Status.ACCEPTED
                    )
                    self.stdout.write(f"  {user.username} is now friends with {friend.username}")

        # === Create Favorite Game Lists ===
        self.stdout.write("Creating favorite game lists...")
        for user in users:
            # Give each user 1 or 2 preferred themes to make their tastes more realistic
            preferred_themes = random.sample(GAME_THEMES, k=random.randint(1, 2))
            preferred_theme_names = [t['theme'] for t in preferred_themes]

            # User will favorite mostly from their preferred themes
            preferred_games = [g for g in games if g.theme_name in preferred_theme_names]
            other_games = [g for g in games if g.theme_name not in preferred_theme_names]

            # Select 70% from preferred, 30% from others
            total_favorites = random.randint(6, 12)
            num_preferred = int(total_favorites * 0.7)
            num_other = total_favorites - num_preferred

            favorites_to_add = []
            favorites_to_add.extend(random.sample(preferred_games, k=min(num_preferred, len(preferred_games))))
            favorites_to_add.extend(random.sample(other_games, k=min(num_other, len(other_games))))

            fav_list, _ = FavoriteGamesByUser.objects.get_or_create(user=user)
            fav_list.games.set(favorites_to_add)
            self.stdout.write(f"  Created favorites for {user.username} (Prefers: {', '.join(preferred_theme_names)})")

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))