import json, os, shutil
log = json.load(open('/Users/amir/Desktop/Inch of Shadow/Inchofshadowcode/plans/cleanup/trash-a-log-20261105-041355.json'))
for e in log:
    if os.path.exists(e['to']) and not os.path.exists(e['from']):
        os.makedirs(os.path.dirname(e['from']), exist_ok=True); shutil.move(e['to'], e['from'])
print('restored', len(log))
