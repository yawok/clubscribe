from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin


class Venue(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=48)
    description = models.TextField()
    polygon = models.PolygonField()

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def _create_user(self, first_name, last_name, email, password, **extra_fields):
        use_in_migrations = True

        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(first_name, last_name, email, password, **extra_fields)

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(first_name, last_name, email, password, **extra_fields)


class User(AbstractUser, PermissionsMixin):
    username = None
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    merchant = models.ForeignKey("Merchant", on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()
    
    def is_merchant(self):
        if self.merchant:
            return True
        return False


class Merchant(models.Model):
    merchant_id = models.CharField()
    access_token = models.CharField()
    refresh_token = models.CharField()
    expiry_date = models.DateTimeField()

    def __str__(self):
        return self.merchant_id

class ClubManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class Club(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=128)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    
    objects = ClubManager()

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.slug,)


class Event(models.Model):
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=48)
    description = models.TextField(null=True, blank=True)
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Membership(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_id = models.CharField()
    subscription_id = models.CharField()

    def __str__(self):
        return f"{self.subscriber} - {self.club}"


class SubscriptionPlan(models.Model):
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=100)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name
