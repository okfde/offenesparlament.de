
from fabric.api import *

env.hosts = ['norton.pudo.org']
deploy_dir = '/var/www/offenesparlament.de/'
remote_user = 'fl'
pip_cmd = deploy_dir + 'bin/pip '

def deploy():
    run('mkdir -p ' + deploy_dir + 'dumps')
    run('pg_dump -f ' + deploy_dir + 'dumps/opa_web-`date +%Y%m%d`.sql opa_web')
    with cd(deploy_dir + 'src/offenesparlament'):
        run('git pull')
        run('git reset --hard HEAD')
        run(pip_cmd + 'install -r pip-requirements.txt')
    sudo('supervisorctl reread')
    sudo('supervisorctl offenesparlament restart')
    run('curl -X PURGEDOMAIN http://offenesparlament.de')

def install():
    sudo('rm -rf ' + deploy_dir)
    sudo('mkdir -p ' + deploy_dir)
    sudo('chown -R ' + remote_user + ' ' + deploy_dir)
    put('deploy/*', deploy_dir)

    sudo('mv ' + deploy_dir + 'nginx.conf /etc/nginx/sites-available/offenesparlament.de')
    sudo('service nginx restart')

    sudo('ln -sf /etc/nginx/sites-available/offenesparlament.de /etc/nginx/sites-enabled/offenesparlament.de')
    sudo('ln -sf ' + deploy_dir + 'supervisor.conf /etc/supervisor/conf.d/offenesparlament.de.conf')
    run('mkdir ' + deploy_dir 'logs')
    sudo('chown -R www-data.www-data ' + deploy_dir 'logs')

    run('virtualenv ' + deploy_dir)
    run(pip_cmd + 'install gunicorn gevent')
    run(pip_cmd + 'install -e git+git@github.com:pudo/offenesparlament.git#egg=offenesparlament')
    
    deploy()
    
    run(pip_cmd + 'install datafreeze')

