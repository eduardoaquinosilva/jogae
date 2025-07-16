from django import forms
from .models import Game, Genre, Tag, Rating



class GameForm(forms.ModelForm):
    genres_text = forms.CharField(
        label="Genres",
        help_text="Separe os gêneros por vírgula.",
        required=False
    )
    tags_text = forms.CharField(
        label="Tags",
        help_text="Separe as tags por vírgula.",
        required=False
    )

    class Meta:
        model = Game
        fields = ['title', 'description', 'picture', 'genres_text', 'tags_text']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['genres_text'].initial = ', '.join(
                [g.name for g in self.instance.genres.all()]
            )
            self.fields['tags_text'].initial = ', '.join(
                [t.name for t in self.instance.tags.all()]
            )


    def save(self, commit=True):
        # First, save the game instance to get an object to work with
        game = super().save(commit=False)
        
        # We need to save the game instance before we can add ManyToMany relationships
        if commit:
            game.save()

        # Handle Genres
        if 'genres_text' in self.cleaned_data:
            genre_names = [name.strip() for name in self.cleaned_data['genres_text'].split(',') if name.strip()]
            game.genres.clear()
            for name in genre_names:
                # get_or_create returns a tuple: (object, created_boolean)
                genre, _ = Genre.objects.get_or_create(name__iexact=name, defaults={'name': name})
                game.genres.add(genre)

        # Handle Tags
        if 'tags_text' in self.cleaned_data:
            tag_names = [name.strip() for name in self.cleaned_data['tags_text'].split(',') if name.strip()]
            game.tags.clear()
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name__iexact=name, defaults={'name': name})
                game.tags.add(tag)

        # Final save for the ManyToMany fields
        if commit:
            self.save_m2m()

        return game


class RatingForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ['body', 'rating']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 5, 'step': 0.5}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Deixe seu comentário aqui...'}),
        }