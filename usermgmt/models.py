from django.db import models
from django.contrib.auth.models import User
from tagging.fields import TagField

class Author(models.Model):
    user = models.OneToOneField(User)
    bio = models.TextField(blank = True)
    friends = models.ManyToManyField('Author', blank = True, null = True)
    tags = TagField()

    def get_absolute_url(self):
        return "/author/%s/" % self.user.username
