from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Count, Prefetch


class PostQuerySet(models.QuerySet):
    def popular_posts(self):
        order_by_posts = (self.annotate(likes_count=Count('likes')).
                          order_by('-likes_count').
                          prefetch_related('author')
                          )
        return order_by_posts

    def fetch_with_comments_count(self):
        id_posts = [post.id for post in self]
        comments_posts = Post.objects.filter(id__in=id_posts).annotate(comments_count=Count('comments'))
        id_and_comment_posts = comments_posts.values_list('id', 'comments_count')
        count_for_id = dict(id_and_comment_posts)
        for post in self:
            post.comments_count = count_for_id[post.id]
        return self

    def fresh_posts(self):
        order_by_posts = (self.annotate(comments_count = Count('comments')).
                          order_by('-published_at')
                          .prefetch_related('author')
                          )

        return order_by_posts


class Post(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    text = models.TextField("Текст")
    slug = models.SlugField("Название в виде url", max_length=200)
    image = models.ImageField("Картинка")
    published_at = models.DateTimeField("Дата и время публикации")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        limit_choices_to={'is_staff': True})
    likes = models.ManyToManyField(
        User,
        related_name="liked_posts",
        verbose_name="Кто лайкнул",
        blank=True)

    objects = PostQuerySet.as_manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'


class Comment(models.Model):
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        verbose_name="Пост, к которому написан",
        related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор")

    text = models.TextField("Текст комментария")
    published_at = models.DateTimeField("Дата и время публикации")

    def __str__(self):
        return f"{self.author.username} under {self.post.title}"

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
