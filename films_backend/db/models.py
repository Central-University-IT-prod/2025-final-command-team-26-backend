from tortoise import fields
from tortoise.models import Model


class Users(Model):
    id = fields.UUIDField(pk=True)
    token = fields.CharField(max_length=255, null=True)
    login = fields.CharField(max_length=255, unique=True)
    password_hash = fields.TextField(null=True)

    films: fields.ReverseRelation['Films']
    users_films: fields.ReverseRelation['UsersFilms']

    playlists: fields.ReverseRelation['Playlists']

    def __str__(self):
        return self.login


class Films(Model):
    id = fields.UUIDField(pk=True)
    title = fields.TextField()
    year = fields.IntField(null=True)
    tmdb_id = fields.IntField(null=True)
    users: fields.ManyToManyRelation['Users'] = fields.ManyToManyField(
        model_name='models.Users',
        through='usersfilms',
        related_name='films',
    )
    genres: fields.ManyToManyRelation['Genres'] = fields.ManyToManyField(
        model_name='models.Genres',
        through='films_genres',
        related_name='films',
    )

    users_films: fields.ReverseRelation['UsersFilms']

    def __str__(self):
        return self.title


class UsersFilms(Model):
    id = fields.UUIDField(pk=True)
    user: fields.ForeignKeyRelation['Users'] = fields.ForeignKeyField(
        'models.Users', related_name='users_films'
    )
    film: fields.ForeignKeyRelation['Films'] = fields.ForeignKeyField(
        'models.Films', related_name='users_films'
    )
    note = fields.TextField(null=True)
    link = fields.TextField(null=True)
    is_viewed = fields.BooleanField(default=False)
    view_date = fields.DateField(null=True)
    created_date = fields.DatetimeField(auto_now_add=True)

    playlists: fields.ReverseRelation['Playlists']


class Genres(Model):
    id = fields.UUIDField(pk=True)
    tmdb_id = fields.IntField()
    title = fields.CharField(max_length=255)

    films: fields.ReverseRelation['Films']

    def __str__(self):
        return self.title


class Playlists(Model):
    id = fields.UUIDField(pk=True)
    title = fields.CharField(max_length=255)
    user: fields.ForeignKeyRelation['Users'] = fields.ForeignKeyField(
        'models.Users', related_name='playlists'
    )
    films: fields.ManyToManyRelation['UsersFilms'] = fields.ManyToManyField(
        'models.UsersFilms',
        related_name='playlists',
    )

    def __str__(self):
        return self.title
