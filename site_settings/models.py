from django.db import models

# Create your models here.


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.__class__.objects.exclude(pk=self.pk).delete()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # запрещаем удаление

    @classmethod
    def load(cls):
        return cls.objects.first() or cls.objects.create()

class GeneralSettings(SingletonModel):
    site_title = models.CharField(max_length=200, verbose_name="Заголовок сайта")
    site_description = models.TextField(verbose_name="Описание сайта")
    contact_email = models.EmailField(verbose_name="Email для связи")
    contact_phone = models.CharField(max_length=20, verbose_name="Телефон для связи")

    class Meta:
        verbose_name = "Общие настройки"
        verbose_name_plural = "Общие настройки"

    def __str__(self):
        return "Общие настройки сайта"


class HomePageSettings(SingletonModel):
    header_title = models.CharField(max_length=200, verbose_name="Заголовок на главной")
    header_subtitle = models.CharField(max_length=300, verbose_name="Подзаголовок")
    about_text = models.TextField(verbose_name="О нас")
    mission_text = models.TextField(verbose_name="Миссия")

    class Meta:
        verbose_name = "Настройки главной страницы"
        verbose_name_plural = "Настройки главной страницы"

    def __str__(self):
        return "Настройки главной страницы"


class SocialLinks(SingletonModel):
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Социальные сети"
        verbose_name_plural = "Ссылки на социальные сети"

    def __str__(self):
        return "Социальные ссылки"


class SEOSettings(SingletonModel):
    meta_title = models.CharField(max_length=255)
    meta_description = models.TextField()
    meta_keywords = models.TextField(help_text="Через запятую")

    class Meta:
        verbose_name = "SEO-настройки"
        verbose_name_plural = "SEO-настройки"

    def __str__(self):
        return "SEO-настройки"


class FooterSettings(SingletonModel):
    footer_text = models.TextField(verbose_name="Текст в подвале")
    footer_links = models.JSONField(default=list, verbose_name="Ссылки в подвале")

    class Meta:
        verbose_name = "Настройки подвала"
        verbose_name_plural = "Настройки подвала"

    def __str__(self):
        return "Настройки подвала"
