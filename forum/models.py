from django.db import models
from django.contrib.auth.models import User

class ForumUser(models.Model):
    user = models.OneToOneField(User, primary_key = True)
    signature = models.TextField(blank = True)

class Forum(models.Model):
    slug = models.SlugField(primary_key = True)
    name = models.CharField(max_length = 120)
    description = models.CharField(max_length = 500)
    parent = models.ForeignKey('Forum', blank = True, null = True)
    moderators = models.ManyToManyField(User)
    users_can_post = models.BooleanField()

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        if self.slug == '__root__':
            return '/forums/'
        else:
            return '/forums/%s/' % self.slug

class Post(models.Model):
    forum = models.ForeignKey('Forum')
    parent = models.ForeignKey('Post', blank = True, null = True)
    owner = models.ForeignKey(User)
    is_sticky = models.BooleanField()
    users_can_reply = models.BooleanField(default = True)
    title = models.CharField(max_length = 250)
    body = models.TextField()
    ctime = models.DateTimeField(auto_now_add = True)
    mtime = models.DateTimeField(auto_now = True)
    muser = models.ForeignKey(User, blank = True, null = True, related_name = 'modified_post')
    mreason = models.CharField(max_length = 250, blank = True, null = True)

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['-is_sticky', 'ctime']

class PM(models.Model):
    user_to = models.ForeignKey(User, related_name = 'user_to')
    user_from = models.ForeignKey(User, related_name = 'user_from')
    parent = models.ForeignKey('PM', blank = True, null = True)
    title = models.CharField(max_length = 250)
    body = models.TextField()
    ctime = models.DateTimeField(auto_now_add = True)
    is_read = models.BooleanField()

    def __unicode__(self):
        return self.title

    def has_unread(self):
        to_ret = not self.is_read
        for p in self.pm_set.all():
            # check for unread PMs
            to_ret = to_ret or not p.is_read
        return to_ret

    class Meta:
        ordering = ['ctime']
