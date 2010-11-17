AS_USER = 'www-data'
ROOT_PATH = '/var/praekelt/mobiletv'
BUILDOUT_REPO = 'git@github.com:praekelt/buildouts.git'
REPO_BRANCH = 'mobiletv-sa'
SHARED_RESOURCES = [
    'downloads', 
    'eggs', 
    'log',
    'production_main_media/content_images', 
    'production_main_media/ingesting_clip_resources', 
    'production_main_media/photologue', 
    'qa_media/content_images', 
    'qa_media/ingesting_clip_resources', 
    'qa_media/photologue',
]

PRODUCTION_HOST = 'plusshaun@localhost'
PRODUCTION_FCGI_CONTROL_SCRIPT = 'mobiletv_production_main.fcgi'

QA_HOST = 'localhost'
QA_FCGI_CONTROL_SCRIPT = 'mobiletv_qa.fcgi'
