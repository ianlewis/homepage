#:coding=utf-8:

import base64


tmpl = """apiVersion: v1
kind: Secret
metadata:
  name: homepage-backup-secret
data:
  db-user: %(dbuser)s
  db-password: %(dbpass)s
  gsutil-config: %(gsutil_conf)s"""


def main():
    with open("./gsutil.conf") as gsutil_conf_file:
        gsutil_conf = gsutil_conf_file.read()
    print(tmpl % {
        "dbuser": base64.b64encode("root"),
        "dbpass": base64.b64encode("yourpassword"),
        "gsutil_conf": base64.b64encode(gsutil_conf),
    })


if __name__ == '__main__':
    main()
