from django.db import models

class DatasetMetadata(models.Model):
    filename = models.CharField(max_length=100)
    download_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename, self.download_date

class DatasetFiles(models.Model):
    dataset = models.ForeignKey(DatasetMetadata, on_delete=models.CASCADE)
    csv_file = models.FileField(upload_to='csv_files/')

    def __str__(self):
        return self.csv_file.name