# User as which to perform the deploy. Used to setup permissions appropriately and to clone from github.
AS_USER = 'www-data'

#Python command with which to boostrap Buildout.
PYTHON_EXEC = 'python2.6'

# Root path in which to perform the deploy. qa/production/current/release structure will be created within this path.
ROOT_PATH = '/var/praekelt/project_name'

# Buildout repo with which to perform the deploy.
BUILDOUT_REPO = 'git@github.com:praekelt/something.git'

# Buildout repo branch with which to perform the deploy.
REPO_BRANCH = 'master'

# Resources to copy accross from the current release to the new releaseon each deploy.
SHARED_RESOURCES = [
    'downloads', 
    'eggs', 
    'log',
    'media', 
]

# Production hostname on which to perform production deploys.
PRODUCTION_HOST = 'localhost'

# Production FCGI control script name.
PRODUCTION_FCGI_CONTROL_SCRIPT = 'project_name_main.fcgi'

# QA hostname on which to perform qa deploys.
QA_HOST = 'localhost'

# QA FCGI control script name.
QA_FCGI_CONTROL_SCRIPT = 'project_name_qa.fcgi'
