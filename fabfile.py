"""
Simple Fabric script remotely deploying Buildouts.
NOTE: For this to work the remote login user should not have a ~/.buildout path and default configuration.
NOTE: This script does not currently do rollbacks or automatic recoveries on a fail. If anything goes wrong during the deploy you'll have to get your feet wet and manually perform the process.
"""

from __future__ import with_statement
from datetime import datetime
import os

from fabric.api import *
from fabric.context_managers import *
from fabric.contrib.console import confirm

import deploy_conf

def _clone_buildout(release_path, timestamp):
    """
    Clone buildout switch to branch and return HEAD rev hash.
    """
    with cd(release_path):
        sudo('git clone %s %s' % (deploy_conf.BUILDOUT_REPO, timestamp), user=deploy_conf.AS_USER)
        with cd(timestamp):
            sudo('git checkout -b %s origin/%s' % (deploy_conf.REPO_BRANCH, deploy_conf.REPO_BRANCH), user=deploy_conf.AS_USER)
            return sudo('git rev-parse HEAD', user=deploy_conf.AS_USER)

def _run_buildout(new_release_path, deploy_type):
    with cd(new_release_path):
        conf_file = '%s.cfg' % deploy_type.lower()
        sudo('%s bootstrap.py -c %s' % (deploy_conf.PYTHON_EXEC, conf_file), user=deploy_conf.AS_USER)
        sudo('./bin/buildout -v -c %s' % conf_file, user=deploy_conf.AS_USER)

def _copy_shared_resources(current_release_path, new_release_path):
    if not current_release_path:
        return None

    for shared_resource in deploy_conf.SHARED_RESOURCES:
        path = os.path.join(current_release_path, shared_resource)
        with cd(new_release_path):
            dir_path = os.path.split(shared_resource)[0]
            if dir_path != '':
                sudo('mkdir -p %s' % dir_path, user=deploy_conf.AS_USER)
            with settings(warn_only=True):
                if dir_path != '':
                    sudo('cp -r %s %s' % (path, dir_path), user=deploy_conf.AS_USER)
                else:
                    sudo('cp -r %s .' % path, user=deploy_conf.AS_USER)

def _get_current_release_path(path):
    with cd(path):
        with settings(warn_only=True):
            result = sudo('ls -l current', user=deploy_conf.AS_USER)
            if result.failed:
                return None
            else:
                return result.split('-> ')[-1]
                
def _qa_rev_match(rev):
    path = os.path.join(deploy_conf.ROOT_PATH, 'qa')
    with settings(host_string=deploy_conf.QA_HOST, warn_only=True):
        qa_current_release_path = _get_current_release_path(path)
        if not qa_current_release_path:
            return False
        with cd(qa_current_release_path):
            qa_rev = sudo('git rev-parse HEAD', user=deploy_conf.AS_USER)
            return qa_rev == rev
        
def _deploy(deploy_type):
    """
    Deploys a Buildout based on provided deploy_conf.py.

    The process is as follows:
        * Create a new release folder structure as follows <ROOT_PATH>/<deploy_type>/releases/<release_timestamp>
        * Clone Buildout specified in BUILDOUT_REPO and switch to branch specified in REPO_BRANCH.
        * Copy shared resources specified in SHARED_RESOURCES from current release to new release path.
        * Run the Buildout.
        * Stop Nginx and old FCGI processes.
        * Update current symlink to point to new release.
        * Start Nginx and new FCGI processes.
    """
    release_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Build paths.
    path = os.path.join(deploy_conf.ROOT_PATH, deploy_type.lower())
    release_path = os.path.join(path, 'releases')
    current_release_path = _get_current_release_path(path)
    new_release_path = os.path.join(release_path, release_timestamp)
    
    # Ask for deploy confirmation and kickoff process or abort.
    if confirm("This will release %s's %s branch to %s's %s path and restart appropriate %s processes. Continue?" % (
            deploy_conf.BUILDOUT_REPO,
            deploy_conf.REPO_BRANCH,
            env.host_string,
            new_release_path,
            deploy_type,
        )):

        # Confirm continue when no previous release is found.
        if not current_release_path:        
            if not confirm('It looks like there is no current release. This means no shared resources can be copied to this new release. Continue anyway?'):
                abort("No current release found. Aborting at user request.")

        # Create release path. 
        sudo('mkdir -p %s' % release_path, user=deploy_conf.AS_USER)

        # Clone buildout.
        rev = _clone_buildout(release_path, release_timestamp)

        # If this is a production release confirm continue if the current rev has not been released to QA.
        if deploy_type == 'PRODUCTION':
            if not _qa_rev_match(rev):
                if not confirm('It looks like the current rev has not been released to QA yet. Are you trying to sneak untested code through to production? Shame on you! Continue anyway?'):
                    abort("No rev found for current release on QA. Aborting at user request.")

        # Copy shared resources.
        _copy_shared_resources(current_release_path, new_release_path)

        # Run buildout.
        _run_buildout(new_release_path, deploy_type)
    
        # Stop Nginx and old FCGI processes.
        sudo('/etc/init.d/nginx stop')
        with settings(warn_only=True):
            sudo('/etc/init.d/%s stop' % getattr(deploy_conf, '%s_FCGI_CONTROL_SCRIPT' % deploy_type))

        # Set current to new release.
        with cd(path):
            with settings(warn_only=True):
                sudo('rm current')
            sudo('ln -s %s current' % new_release_path)
    
        # Start Nginx and new FCGI processes.
        with settings(warn_only=True):
            sudo('/etc/init.d/%s start' % getattr(deploy_conf, '%s_FCGI_CONTROL_SCRIPT' % deploy_type))
        sudo('/etc/init.d/nginx start')

@hosts(deploy_conf.PRODUCTION_HOST)
def deploy_production():
    _deploy(deploy_type='PRODUCTION')

@hosts(deploy_conf.QA_HOST)
def deploy_qa():
    _deploy(deploy_type='QA')
