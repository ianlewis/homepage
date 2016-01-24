#:coding=utf-8:

import sys
import base64


tmpl = """apiVersion: v1
kind: Secret
metadata:
  name: cron-secrets
data:
  crontab: %(crontab)s
  backup.yaml: %(backup_yaml)s
"""


def main(crontab_path):
    with open("../backup/backup.yaml") as backup_yaml_file:
        backup_yaml = backup_yaml_file.read()
    with open(crontab_path) as crontab_file:
        crontab = crontab_file.read()
    print(tmpl % {
        "crontab": base64.b64encode(crontab),
        "backup_yaml": base64.b64encode(backup_yaml),
    })


if __name__ == '__main__':
    main(sys.argv[1])
