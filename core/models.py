from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(unique=True, verbose_name="Транскрипция")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Room(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='rooms', verbose_name="Категория")
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер комнаты")
    capacity = models.PositiveIntegerField(verbose_name="Количество гостей")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за ночь")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='rooms/', verbose_name="Фотография")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для бронирования")

    def __str__(self):
        return f"№{self.number} - {self.category.name}"

    class Meta:
        verbose_name = "Номер"
        verbose_name_plural = "Номера"

class ExtraService(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название услуги")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Дополнительная услуга"
        verbose_name_plural = "Дополнительные услуги"

    def __str__(self):
        return f"{self.name} ({self.price} ₽)"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('canceled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Клиент")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings', verbose_name="Номер")
    check_in = models.DateField(verbose_name="Дата заезда")
    check_out = models.DateField(verbose_name="Дата выезда")
    guests = models.PositiveIntegerField(verbose_name="Количество гостей")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая цена", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    full_name = models.CharField(max_length=150, null=True, blank=True, verbose_name="ФИО гостя")
    passport = models.CharField(max_length=100, null=True, blank=True, verbose_name="Паспортные данные")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Контактный телефон")
    email_guest = models.EmailField(null=True, blank=True, verbose_name="Email гостя")
    extra_services = models.ManyToManyField(ExtraService, blank=True, verbose_name="Доп. услуги")

    def clean(self):
        if self.check_in >= self.check_out:
            raise ValidationError("Дата выезда должна быть позже даты заезда!")

        if self.check_in < timezone.now().date():
            raise ValidationError("Нельзя забронировать номер в прошлом!")

    def save(self, *args, **kwargs):
        if not self.total_price:
            nights = (self.check_out - self.check_in).days
            self.total_price = self.room.price_per_night * nights
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Бронь {self.id} - {self.user.username}"

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
