from django.db import models

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

#Address model
class Address(models.Model):
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100)
    city = models.CharField(max_length=30)
    state = models.CharField(max_length=30)
    country = models.CharField(max_length=30)
    zip_code = models.CharField(max_length=6)

#Model manager
class EMAUserManager(BaseUserManager):

    def create_user(self, email, password, **fields):
        
        if not email:
            raise ValueError('Email entry required!')
        if not password:
            raise ValueError('Password entry required!')

        user = self.model(
            email = self.normalize_email(email),
            **fields
        )
        user.set_password(password)

        user.save()
        return user

    def create_manager(self, email, password, **fields):
        fields.setdefault('role','Manager')
        return self.create_user(email,password,**fields)

    def create_superuser(self, email, password, **fields):
        fields.setdefault('role','SuperUser')
        fields.setdefault('is_staff',True)
        return self.create_user(email, password, **fields)

#User model
class EMAUser(AbstractBaseUser):

    USER_ROLES = (
        ('Employee','Employee'),
        ('Manager','Manager'),
        ('SuperUser','SuperUser')
    )

    role = models.CharField(max_length=10,choices=USER_ROLES, default='Employee')

    email = models.EmailField(max_length=60,unique=True)
    phone = models.CharField(max_length=10,unique=True)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    address = models.OneToOneField(Address, on_delete=models.CASCADE)

    date_created = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']

    objects = EMAUserManager()

    def __str__(self):
        return self.email