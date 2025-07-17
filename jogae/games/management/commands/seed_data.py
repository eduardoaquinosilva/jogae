import random
import os
import uuid
from django.conf import settings
import csv
from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files import File
from django.contrib.auth import get_user_model
from games.models import Game, Genre, Tag, Rating
from app_profile.models import Friendship
from app_biblioteca.models import FavoriteGamesByUser

User = get_user_model()

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
        Rating.objects.all().delete()
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
        self.stdout.write("Creating genres...")
        genres_db = {}
        genre_csv_file_path = os.path.join(settings.BASE_DIR, 'games', 'data', 'genres.csv')
        try:
            with open(genre_csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    genre_id = row['genre_id']  # Assuming 'genre_id' column exists
                    genre_name = row['genre']
                    genre, created = Genre.objects.get_or_create(id=genre_id, defaults={'name': genre_name})
                    if created:
                        self.stdout.write(f"  Created genre: {genre_name} with ID: {genre_id}")
                    else:
                        self.stdout.write(f"  Genre '{genre_name}' already exists (ID: {genre_id})")
                    genres_db[genre_name] = genre  # Store by name for easy lookup later
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"Genres CSV file not found at: {genre_csv_file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing genres CSV file: {e}"))
            return
        # === Create Games ===
        self.stdout.write("Creating games...")
        games = []

        # Load data from CSV
        csv_file_path = os.path.join(settings.BASE_DIR, 'games', 'data', 'games_data.csv')
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:  # Specify encoding
                reader = csv.DictReader(file)
                for row in reader:
                    title = row['name']
                    genre_name = row['genre']
                    description = row['summary']
                    
                    # Split genre string by spaces
                    genre_names = genre_name.split()

                    game = Game.objects.create(title=title, description=description, user=random.choice(users))

                    # Add genres
                    for name in genre_names:
                        if name not in genres_db:
                            genres_db[name] = Genre.objects.create(name=name)
                        game.genres.add(genres_db[name])




                    # Create 'PC' tag if it doesn't exist and add it
                    pc_tag, _ = Tag.objects.get_or_create(name='PC')

                    game.tags.add(pc_tag)  # Assuming 'PC' tag exists

                    games.append(game)
                    self.stdout.write(f"  Created game: {game.title}")
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"CSV file not found at: {csv_file_path}"))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error processing CSV file: {e}"))
            return
        
        # === Create Ratings ===
        self.stdout.write("Creating ratings...")
        for game in games:
            # Have 1 to 5 users rate each game
            raters = random.sample(users, k=random.randint(1, 5))
            for rater in raters:
                Rating.objects.create(
                    game=game,
                    user=rater,
                    body=f"This is a sample comment for {game.title} by {rater.username}.",
                    rating=round(random.uniform(2.0, 5.0), 1)
                )

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
            # Give each user a random number of favorite games from the created list
            if not games:
                self.stdout.write(self.style.WARNING("  No games were created, skipping favorite list creation."))
                break
            
            num_favorites = random.randint(5, min(15, len(games)))
            favorites_to_add = random.sample(games, k=num_favorites)

            fav_list, _ = FavoriteGamesByUser.objects.get_or_create(user=user)
            fav_list.games.set(favorites_to_add)
            self.stdout.write(f"  Added {len(favorites_to_add)} favorite games for {user.username}")

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database!'))