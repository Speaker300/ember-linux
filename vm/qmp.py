#!/usr/bin/env python3
import json, socket, sys, time
sock_path=sys.argv[1]
cmds=sys.argv[2:]
s=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sock_path)
f=s.makefile('rwb', buffering=0)
def recv():
    line=f.readline()
    if not line: raise SystemExit('QMP closed')
    return json.loads(line)
print(recv())
f.write(b'{"execute":"qmp_capabilities"}\n')
print(recv())
for c in cmds:
    if c.startswith('screendump:'):
        path=c.split(':',1)[1]
        f.write((json.dumps({'execute':'screendump','arguments':{'filename':path}})+'\n').encode())
    elif c.startswith('human-monitor-command:'):
        cmd=c.split(':',1)[1]
        f.write((json.dumps({'execute':'human-monitor-command','arguments':{'command-line':cmd}})+'\n').encode())
    else:
        f.write((json.dumps({'execute':c})+'\n').encode())
    print(recv())
s.close()
