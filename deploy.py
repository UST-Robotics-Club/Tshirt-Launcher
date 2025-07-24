import os
import paramiko
import time
ssh = paramiko.SSHClient() 
ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
host = "10.3.141.1"
#host = "169.254.15.253"
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    print("Trying wifi")
    host = "10.3.141.1"
    ssh.connect(host, username="ustrobotics", password="ustrobotics2")
except:
    print("Trying ethernet")
    host = "169.254.15.253"
    ssh.connect(host, username="ustrobotics", password="ustrobotics2")

sftp = ssh.open_sftp()
local_base = "c:\\Users\\lukeb\\Documents\\Tshirt-Launcher"
remote_base = "/home/ustrobotics/Documents"

for root, dirs, files in os.walk(local_base):
    if '.git' in dirs:
        dirs.remove('.git')

    rel_path = os.path.relpath(root, local_base)
    remote_path = os.path.join(remote_base, rel_path).replace("\\", "/")

    try:
        sftp.listdir(remote_path)
    except IOError:
        sftp.mkdir(remote_path)

    for file in files:
        local_file = os.path.join(root, file)
        remote_file = os.path.join(remote_path, file).replace("\\", "/")
        print(f"Uploading {local_file} to {remote_file}")
        sftp.put(local_file, remote_file)

sftp.close()

shell = ssh.invoke_shell(width=160, height = 80)
shell.send("sudo pkill robot_main.py\n")
time.sleep(0.5)
shell.send("/home/ustrobotics/Documents/bin/python /home/ustrobotics/Documents/robot_main.py\n")

while True:
    d = shell.recv(100).decode()
    print(str(d), end='')
    if len(d) == 0:
        break
ssh.close()
print("Exited")
