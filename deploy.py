import os
import paramiko

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
stdin, stdout, stderr = ssh.exec_command('sudo bash')
stdin.write("sudo pkill -9 -f robot_main.py'")

sftp = ssh.open_sftp()
files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    tp = "c:\\Users\\lukeb\\Documents\\Tshirt-Launcher\\"+f
    print(tp)
    sftp.put(tp, f"/home/ustrobotics/Documents/{f}")
sftp.close()

shell = ssh.invoke_shell(width=160, height = 80)
shell.send("/home/ustrobotics/Documents/bin/python /home/ustrobotics/Documents/robot_main.py\n")

while True:
    d = shell.recv(5).decode()
    print(str(d), end='')
    if len(d) == 0:
        break
ssh.close()
print("Exited")
