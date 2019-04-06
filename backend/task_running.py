import sys, os
import time
import paramiko
import json
from django import conf
from concurrent.futures import ThreadPoolExecutor

def ssh_cmd(sub_task_obj):
     host_to_remote_user = sub_task_obj.host_to_remote_user
     try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host_to_remote_user.host.ip,
                           host_to_remote_user.host.port,
                           host_to_remote_user.remote_user.username,
                           host_to_remote_user.remote_user.pwd,
                           timeout=5)
        stdin, stdout, stderr = ssh_client.exec_command(sub_task_obj.task.content)
        print('-----------------stdout&stderr-----------------------------------')
        stdout_res = stdout.read().decode('utf-8')
        stderr_res = stderr.read().decode('utf-8')
        print("stdout_res:",stdout_res)
        print("stderr_res:",stderr_res)
        #sub_task_obj = models.TaskDetail.objects.get(task=task_obj, host_to_remote_user=host_to_remote_user)
        sub_task_obj.result=stderr_res+stdout_res
        if stderr_res:
            sub_task_obj.task_status=2
        else:
            sub_task_obj.task_status=1


     except Exception as e:
         sub_task_obj.result= str(e)
         sub_task_obj.task_status=2
         print(e)
     sub_task_obj.save()

def file_transfer(sub_task_obj, task_data):
    try:
        host = sub_task_obj.host_to_remote_user.host.ip
        port = sub_task_obj.host_to_remote_user.host.port
        username = sub_task_obj.host_to_remote_user.remote_user.username
        password= sub_task_obj.host_to_remote_user.remote_user.pwd
        timeout=5
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, password=password, timeout=timeout)
        sftp_client = paramiko.SFTPClient.from_transport(client.get_transport())

        toPath = task_data["remote_path"]
        if task_data["file_transfer_type"] == 'Send':
            fromPath = task_data["local_path"]
            sftp_client.put(fromPath, toPath)
            result = "%s has been upload to %s successfully!"%(fromPath, toPath)
            sub_task_obj.result = result
            sub_task_obj.task_status = 1
        else:
            filename = toPath.split("/")[-1]
            fromPath = "%s%s/%s"%(conf.settings.DOWNLOADS,sub_task_obj.task.id, filename)
            print(fromPath)
            if not os.path.exists(fromPath):
                os.mkdir("%s%s"%(conf.settings.DOWNLOADS,sub_task_obj.task.id))
            sftp_client.get(toPath, fromPath)
            result = "[%s] has been download to [%s] successfully!"%(toPath, fromPath)
            sub_task_obj.result = result
            sub_task_obj.task_status = 1

        sftp_client.close()
        client.close()
    except Exception as e:
        print(e)
        result = str(e)
        sub_task_obj.result=result
        sub_task_obj.task_status=2
    sub_task_obj.save()



if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(base_dir)
    sys.path.append(base_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TmCrazyEye.settings')
    import django
    django.setup()
    from app01 import models

    if len(sys.argv) == 1:
         exit("task_id is not provided!")
    task_id = sys.argv[1]
    task_obj = models.Task.objects.get(id=task_id)
    task_type = task_obj.task_type
    print(task_type)
    #并发执行任务
    pool = ThreadPoolExecutor(5)
    for sub_task_obj in task_obj.taskdetail_set.all():
        if task_type == 0:
            pool.submit(ssh_cmd, sub_task_obj)
        else:
            task_data = json.loads(task_obj.content)
            pool.submit(file_transfer, sub_task_obj, task_data)

    #ssh_cmd(task_obj)
    #task_obj.content = "task test"
    #time.sleep(8)
    #task_obj.save()
