import paramiko
import yaml


with open('config.yaml', encoding='utf-8') as f:
    data = yaml.safe_load(f)


def ssh_checkout(cmd, text):
    exit_code, out = ssh_getout(cmd)
    if text in out and exit_code == 0:
        return True
    else:
        return False


def ssh_getout(cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(data["host"], data["port"], data["user"], data["passwd"])
    stdin, stdout, stderr = client.exec_command(cmd)
    exit_code = stdout.channel.recv_exit_status()
    out = (stdout.read() + stderr.read()).decode("utf-8")
    client.close()
    return exit_code, out


def upload_files(local_path, remote_path):
    print(f"Загружаем файл {local_path} в каталог {remote_path}")
    transport = paramiko.Transport((data["host"], data["port"]))
    transport.connect(None, data["user"], data["passwd"], )
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_path, remote_path)
    if sftp:
        sftp.close()
    if transport:
        transport.close()


def download_files(remote_path, local_path):
    print(f"Скачиваем файл {remote_path} в каталог {local_path}")
    transport = paramiko.Transport((data["host"], data["port"]))
    transport.connect(None, data["user"], data["passwd"], )
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(remote_path, local_path)
    if sftp:
        sftp.close()
    if transport:
        transport.close()
