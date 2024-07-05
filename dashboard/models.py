from django.db import models

TASK_STATE = (
    ("PENDING","PENDING"),
    ("STARTED", "STARTED"),
    ("FINISHED", "FINISHED"),
    ("FAILED", "FAILED"),
)

class CompanyData(models.Model):
    company_name = models.CharField(max_length=150,blank=True,null=True)
    company_domain = models.CharField(max_length=150,blank=True,null=True)
    year_founded = models.DateField(null=True,blank=True)
    industry = models.CharField(max_length=100,blank=True,null=True)
    size_range = models.CharField(max_length=20,blank=True,null=True)
    locality = models.CharField(max_length=100,blank=True,null=True)
    country = models.CharField(max_length=50,blank=True,null=True)
    linkedin_url = models.CharField(max_length=100,blank=True,null=True)
    current_estimate = models.PositiveBigIntegerField(blank=True,null=True)
    total_estimate = models.PositiveBigIntegerField(blank=True,null=True)

    def __str__(self):
        return f"{self.pk} : {self.company_name}"
    
class UploadTasks(models.Model):
    task_id = models.CharField(max_length=64)
    task_state = models.CharField( 
        max_length = 20, 
        choices = TASK_STATE, 
        default = 'PENDING'
        ) 
    
    def __str__(self):
        return f"{self.task_id} - {self.task_state}"

class Industry(models.Model):
    industry_name = models.CharField(max_length=150,blank=True,null=True)

    def __str__(self):
        return f"{self.pk} : {self.industry_name}"