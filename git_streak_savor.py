#!/usr/bin/env python

from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser

import argparse
import re
import sh
import logging


def check_project(main_path, project_list):
    for project in project_list:
        path = main_path + project
        git = sh.git.bake(_cwd=path)

        git('pull', 'origin', 'master')
        logging.info('Pulled %s' % project)

        last_mod = git('--no-pager', 'log', '-1', '--pretty=format:%ci')
        logging.info('Last_mod %s' % last_mod)
        git_time_str = re.search('\d{4}-\d{2}-\d{2}', str(last_mod)).group(0) # Magic line
        last_mod_time = datetime.strptime(git_time_str, '%Y-%m-%d')

        # Check if last mod == Today
        if current.date() - last_mod_time.date() == timedelta(0):
            logging.info('Found a new modified project <%s>, abort update' % project)
            return False
    return True


def update_project(target_path):
    with open(target_path, 'a') as tf:
        tf.write(str(current.date())+' ')

    path = target_path.rsplit('/',1)[0]
    git = sh.git.bake(_cwd=path)

    if args.commit:
        git('add', target_path)
        git('commit', '-m', 'Keep streak on %s' % str(current.date()))
        git('push', 'origin', 'master')
        logging.info('Pushed to target file at %s' % str(current))
    else:
        git('checkout', target_path)
        logging.info('Abort and revert')


#######################################################
# MAIN
#######################################################

config_parser = SafeConfigParser()
config_parser.read('config')

arg_parser = argparse.ArgumentParser(description='Save my github streak.')
arg_parser.add_argument('-c', '--commit', action='store_true',
                        help='Actually commit the change (default: no)')
arg_parser.add_argument('-v', '--verbose', action='store_true',
                        help='Increase output verbosity')
args = arg_parser.parse_args()

LOG_PATH = config_parser.get('Path', 'log_path') + 'git_streak_savor.log'

if args.verbose:
    logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG)
else:
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO)

main_path    = config_parser.get('Path', 'main_path')
target_path  = config_parser.get('Path', 'target_path')
project_list = [config_parser.get('Project', option) for option in config_parser.options('Project')]

current = datetime.today()

logging.info( '='*12 + str(current) + '='*12 )

if check_project(main_path, project_list):
    update_project(target_path)
logging.info( '='*22 + ' Done ' + '='*22 + '\n')
