echo "Apply database migrations"
python /usr/src/app/manage.py migrate
echo "=============================================="

echo "Starting server"
uwsgi /usr/src/app/uwsgi.ini
