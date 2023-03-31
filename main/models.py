from django.db import models


class Batch(models.Model):
    year = models.CharField(max_length=4, unique=True)

    def __str__(self):
        return f"{self.year} Batch"


class Department(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=500, null=True,  blank=True)

    class Meta:
        unique_together = (('batch', 'name'),)

    def __str__(self):
        return f"{self.name} {self.batch.year} Batch"

    @property
    def short_description(self):
        if self.description:
            if len(str(self.description)) > 50:
                return f"{self.description[:50]} ..."
            else:
                return self.description
