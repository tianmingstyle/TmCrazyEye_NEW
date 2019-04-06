import paramiko

#t = paramiko.Transport(("104.153.99.73", 27517))
t = paramiko.Transport(("192.168.2.151", 22))
#t.connect(username='root', password='tmsugar123')
t.connect(username='root', password='123456')
sftp = paramiko.SFTPClient.from_transport(t)
#sftp.get("/root/text.txt", "C:/")
sftp.put("C:/text.txt", "/root/text.txt")
t.close()