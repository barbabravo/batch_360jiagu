#!/usr/bin
#coding=utf8

import os
import time
import sys
import configparser
import getopt
from datetime import datetime, timedelta, date

import logging
import logging.config
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(name="root")

cur_path = os.path.dirname(os.path.realpath(__file__))

config_path=os.path.join(cur_path,'batch.config')
conf=configparser.ConfigParser()
conf.read(config_path)


#测试360加固
def exec_360_jiagu(input_filepath, output_path, keystore, keystore_password, alias, alias_password):
    print(output_path)
    try:
        os.makedirs(output_path)
    except Exception as err:
        logger.warn(err)

    jiagu_cmd = """java -jar jiagu.jar -jiagu %s %s -autosign -automulpkg"""%(input_filepath, output_path)

    result = os.system(jiagu_cmd)

    if not result:
        logger.info("===%s===加固成功"%(input_filepath))
    else:
        logger.error("===%s===加固失败"%(output_path))

def main(argv):
    pcode = ''
    version = ''
    channel = ''

    try:
        opts, args = getopt.getopt(argv,"hp:v:c:",["p=","v=","c="])
    except getopt.GetoptError:
        logger.error('batch.py -p <projectcode> -v <version> -c <channel>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            logger.error('batch.py -p <projectcode> -v <version> -c <channel>')
            sys.exit()
        elif opt in ("-p", "--pcode"):
            pcode = arg
        elif opt in ("-v", "--version"):
            version = arg
        elif opt in ("-c", "--channel"):
            channel = arg
    
    if(len(pcode) == 0):
        logger.error('pcode不可为空')
        sys.exit()
        
    if(len(version) == 0):
        logger.error('version不可为空')
        sys.exit()
            
    logger.info("准备执行：%s -%s -%s"%(pcode, version, channel))

    try:
        username = conf.get("global", "username")
        password = conf.get("global", "password")
        basedir = conf.get("global", "basedir")

        workdir = conf.get(pcode, "workdir")
        source_name = conf.get(pcode, 'source_name')
        target_name = conf.get(pcode, 'target_name')

        channels_str = conf.get(pcode, "channels")
        keystore = conf.get(pcode, 'keystore')
        keystore_password = conf.get(pcode, 'keystore_password')
        alias = conf.get(pcode, 'alias')
        alias_password = conf.get(pcode, 'alias_password')
    except Exception as err:
        logger.error("缺乏必要的参数")
        sys.exit()
        

    os.chdir(basedir)
    os.system("java -jar jiagu.jar -login %s %s"%(username,password))
    os.system('java -jar jiagu.jar -importsign %s %s %s %s'%(keystore, keystore_password, alias, alias_password))
        
    if(len(channel) == 0):
        channels = channels_str.split(",")
        for channel in channels:
            input_filepath = getInputFilePath(basedir, workdir, version, channel, source_name)
            output_path = getOutputPath(basedir, workdir, version, channel)

            exec_360_jiagu(input_filepath, output_path, keystore, keystore_password, alias, alias_password)
            renameFilename(output_path, target_name)
    else:
        # 指定特定渠道
        input_filepath = getInputFilePath(basedir, workdir, version, channel, source_name)
        output_path = getOutputPath(basedir, workdir, version, channel)
        
        exec_360_jiagu(input_filepath, output_path, keystore, keystore_password, alias, alias_password)
        renameFilename(output_path, target_name)


def renameFilename(output_path, target_name):
    file_names = os.listdir(output_path)
    for old_name in file_names:
        os.rename(os.path.join(output_path, old_name), os.path.join(output_path, target_name))

def getInputFilePath(basedir, workdir, version, channel, filename):
    realFolderName = "%s%s"%(channel, version.replace(".", ""))
    print("getInputFilePath", realFolderName)
    return os.path.join(basedir, workdir, version, 'raw', realFolderName, filename)

def getOutputPath(basedir, workdir, version, channel):
    realFolderName = "%s%s"%(channel, version.replace(".", ""))
    return os.path.join(basedir, workdir, version, 'release', realFolderName)


if __name__ == "__main__":
    starttime = datetime.now()

    main(sys.argv[1:])
    
    endtime = datetime.now()
    logger.info('========结束，耗时%d秒========'%((endtime-starttime).seconds))
