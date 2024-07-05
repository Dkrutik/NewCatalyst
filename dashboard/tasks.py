import csv
from catalyst_count.celery import app
from celery import shared_task
from celery.utils.log import get_task_logger
from .models import CompanyData,UploadTasks,Industry
from catalyst_count.celery import app
from datetime import date

# celery -A catalyst_count worker -l info --concurrency=2 --without-gossip -P threads
# 7173426 926.656s

logger = get_task_logger(__name__)

def csv_reader(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row

@app.task(bind=True, default_retry_delay=30, max_retries=3, acks_late=True)
def process_csv(self,file_path):
    task_id = str(self.request.id)
    print(task_id)
    taskObj = UploadTasks.objects.get(task_id = task_id)
    try:
        taskObj.task_state = 'STARTED'
        taskObj.save()
        # =+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+

        batch_size = 15000
        company_data_list = []

        # Fetch existing industries
        existing_industries = set(Industry.objects.values_list('industry_name', flat=True))
        new_industries = set()

        for row in csv_reader(file_path):
            year_founded = int(float(row['year founded'])) if row['year founded'] else None
            company_data_list.append(
                CompanyData(
                    company_name=row['name'].lower(),
                    company_domain=row['domain'].lower(),
                    year_founded=date(year_founded, 1, 1) if year_founded else None,
                    industry=row['industry'].lower(),
                    size_range=row['size range'].lower(),
                    locality=row['locality'].lower(),
                    country=row['country'].lower(),
                    linkedin_url=row['linkedin url'],
                    current_estimate=int(row['current employee estimate']),
                    total_estimate=int(row['total employee estimate']),
                )
            )

            industry_name = row['industry']
            if industry_name and industry_name not in existing_industries:
                new_industries.add(industry_name)

            if len(company_data_list) >= batch_size:
                CompanyData.objects.bulk_create(company_data_list)
                company_data_list = []

        if company_data_list:
            CompanyData.objects.bulk_create(company_data_list)
        
        Industry.objects.bulk_create(
            [Industry(industry_name=name) for name in new_industries]
        )

        # =+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+
        taskObj.task_state = 'FINISHED'
        taskObj.save()
        return True
    except Exception as e:
        logger.info("Exception here: ",file_path)
        self.retry(exc=e)
        taskObj.task_state = 'FAILED'
        taskObj.save()
        return False
