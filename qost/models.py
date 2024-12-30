from django.db import models

from users.models import User


class Xtext(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text


class Post(models.Model):
    post_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts_user')
    title = models.CharField(max_length=35)
    content = models.TextField()
    like = models.IntegerField(default=0)
    post_xtext = models.ManyToManyField(Xtext, related_name='post_xtext')
    post_image = models.ImageField(upload_to='images/post/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    comment_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_user')
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comment_post')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.comment_user} {self.comment_post.id}'
