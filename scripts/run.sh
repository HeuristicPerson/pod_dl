#!/bin/sh

echo '##############################################################'
echo "#                ______      _____                           #"
echo "#               / _  (_)_ __/ _  / ___  _ __                 #"
echo "#               \// /| | '_ \// / / _ \| '_ \                #"
echo "#                / //\ | |_) / //\ (_) | |_) |               #"
echo "#               /____/_| .__/____/\___/| .__/                #"
echo "#                      |_|             |_|                   #"
echo '##############################################################'
echo ""

TAG=$(python -c "import importlib.util; module = importlib.util.spec_from_file_location('constants', '/app/pod_dl/libs'); print i_DL_RETRIES")

echo "Starting zipzop/pod_dl:v1.0.dev 2021-09-21 $TAG"
echo "=============================================================="

# Copying of the sample subscriptions file in case there is no one in the
# downloads dir
SUBS_SRC=/app/configs/subs.tpl
SUBS_DST=/podcasts/subs.txt
if [ ! -f "$SUBS_DST" ]; then
    cp "$SUBS_SRC" "$SUBS_DST"
fi

# Copying cron template with proper value
sed -e "s|%CRON_HOURS%|$CRON_HOURS|" /app/configs/sync_pod.tpl > /app/configs/sync_pod.cron

# Copying pod_dl custom configuration to replace the default one included with the program
cp /app/configs/pod_dl.ini /app/pod_dl

# Finally we launch the cron
export PYTHONUNBUFFERED=1
supercronic -quiet -passthrough-logs /app/configs/sync_pod.cron
