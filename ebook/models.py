from django.contrib.auth.models import User
from django.db import models
from tagging.fields import TagField

class Book(models.Model):
    slug = models.SlugField(primary_key = True)
    title = models.CharField(max_length = 500)
    subtitle = models.CharField(max_length = 500)
    authors = models.ManyToManyField(User)
    blurb = models.TextField()
    published = models.BooleanField(default = false)
    license = models.ForeignKey('License', blank = True, null = True, default = 1)
    featured = models.BooleanField(default = False)
    ctime = models.DateTimeField(auto_now_add = True)
    tags = TagField()

    def get_absolute_url(self):
        return "/%s/" % self.slug

    def __unicode__(self):
        return self.title

    def _agg_stars(self):
        sum = 0
        ctr = 0
        for c in self.chapter_set.all():
            if c.stars != 0.00:
                sum += c.stars
                ctr += 1
        return str(sum / ctr)

    aggregate_stars = property(_agg_stars)

class Chapter(models.Model):
    RATINGS = (
            ('G', 'G'),
            ('PG', 'PG'),
            ('PG-13', 'PG-13'),
            ('R', 'R'),
            ('NC-17', 'NC-17')
            )
    STATES = (
            ('A', 'Outline'),
            ('B', 'Rough Draft'),
            ('C', 'Edited'),
            ('D', 'Completed'),
            ('E', 'Abandoned'),
            )

    title = models.CharField(max_length = 500)
    body = models.TextField()
    authors = models.ManyToManyField(User)
    book = models.ForeignKey('Book')
    parent = models.ForeignKey('Chapter', blank = True, null = True)
    published = models.BooleanField(default = True)
    users_only = models.BooleanField(default = False)
    friends_only = models.BooleanField(default = False)
    screen_comments = models.BooleanField(default = False)
    license = models.ForeignKey('License', blank = True, null = True, default = 1)
    weight = models.IntegerField()
    views = models.IntegerField()
    stars = models.DecimalField(max_digits = 3, decimal_places = 2, default = '0.00')
    rating = models.CharField(max_length = 5, choices = RATINGS)
    state = models.CharField(max_length = 1, choices = STATES, default = 'A')
    ctime = models.DateTimeField(auto_now_add = True)
    tags = TagField()

    def get_absolute_url(self):
        return "/%s/%s/" % (self.book.slug, self.id)

    def get_compound_weight(self):
        to_return = weight
        if self.parent:
            to_return = parent.get_compound_weight() + '.' + to_return
        return to_return

    def __unicode__(self):
        return "%s. %s (%s)" % (self.weight, self.title, self.owner.username)

    class Meta:
        ordering = ['weight']

class Rating(models.Model):
    chapter = models.ForeignKey('Chapter', related_name = 'user_rating')
    owner = models.ForeignKey(User)
    stars = models.IntegerField()

class License(models.Model):
    slug = models.SlugField(unique = True)
    title = models.CharField(max_length = 120)
    description = models.CharField(max_length = 500)
    url = models.URLField(blank = True)
    display = models.CharField(max_length = 120)

    def __unicode__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey('Manifesto')
    parent = models.ForeignKey('Comment', blank = True, null = True)
    owner = models.ForeignKey(User)
    title = models.CharField(max_length = 500, blank = True)
    body = models.TextField()
    published = models.BooleanField(default = True)
    ctime = models.DateTimeField(auto_now_add = True)

    def get_absolute_url(self):
        return "/manifesto/%s/#%s" % (self.post.id, self.id)

################ Signals ###################
from django.contrib.comments.signals import comment_was_posted
from django.core.mail import send_mail

def mail_author_on_comment(sender, **kwargs):
    comment = kwargs['comment']
    message = """
Dear %(recipient)s,

Someone has replied to your post on HTR.  You may view
and reply to this comment by logging in and viewing your post at:

http://htr.mjs-svc.com%(url)s

They said:

    %(body)s

Please do not reply to this email.

~The HTR team
    """ % {'recipient': comment.content_object.owner.username, 'url': comment.content_object.get_absolute_url(), 'body': comment.comment}
    send_mail("Comment on your post: %s" % comment.content_object.title, message, 'mjs+htrcomments@mjs-svc.com', [comment.content_object.owner.email], fail_silently = False)

def mail_comment_parent_author_on_comment(sender, **kwargs):
    comment = kwargs['comment']
    if comment.parent:
        message = """
Dear %(recipient)s,

Someone has replied to your comment on HTR.  You may view
and reply to this comment by logging in and viewing your post at:

http://htr.mjs-svc.com%(url)s

They said:

    %(body)s

Please do not reply to this email.

~The HTR team
        """ % {'recipient': comment.parent.user.username, 'url': comment.content_object.get_absolute_url(), 'body': comment.comment}
        send_mail("Reply to your comment: %s" % comment.content_object.title, message, 'mjs+htrcomments@mjs-svc.com', [comment.parent.user.email], fail_silently = False)

comment_was_posted.connect(mail_author_on_comment)
comment_was_posted.connect(mail_comment_parent_author_on_comment)
