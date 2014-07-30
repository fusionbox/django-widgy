from django.db import models


class Base(models.Model):
    foo = models.AutoField(primary_key=True)

class Child(Base):
    pass
