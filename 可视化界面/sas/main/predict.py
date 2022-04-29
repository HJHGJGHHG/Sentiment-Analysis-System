import os
import time
import paramiko


def predict():
    # 创建一个通道
    transport = paramiko.Transport(('region-11.autodl.com', 20362))
    transport.connect(username='root', password='4R2/taxoIS')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    ssh._transport = transport
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    sftp.put(localpath="D:/Desktop/Sentiment-Analysis-System/可视化界面/sas/new_comments.pkl",
             remotepath="/root/autodl-tmp/SAS/模型/data/new_comments.pkl")
    stdin, stdout, stderr = ssh.exec_command("bash --login -c 'python /root/autodl-tmp/SAS/模型/deploy/predict.py'")
    while True:
        try:
            sftp.get(remotepath="/root/autodl-tmp/SAS/模型/data/result.json",
                     localpath="D:/Desktop/Sentiment-Analysis-System/可视化界面/sas/result.json")
            break
        except FileNotFoundError:
            continue
    if os.path.exists("D:/Desktop/Sentiment-Analysis-System/可视化界面/sas/result.json"):
        stdin, stdout, stderr = ssh.exec_command("bash --login -c 'rm /root/autodl-tmp/SAS/模型/data/new_comments.pkl'")
        stdin, stdout, stderr = ssh.exec_command("bash --login -c 'rm /root/autodl-tmp/SAS/模型/data/result.json'")
        transport.close()
        return
