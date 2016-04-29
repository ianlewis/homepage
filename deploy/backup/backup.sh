#!/bin/sh

mysqldump --host=mysql --user=`cat /etc/secrets/db-user` --password=`cat /etc/secrets/db-password` --single-transaction homepage \
    | bzip2 \
    | /opt/gsutil/gsutil cp - gs://${BUCKET}/${NAMESPACE}.`date +%Y%m%d%H%M%S`.sql.bz2
