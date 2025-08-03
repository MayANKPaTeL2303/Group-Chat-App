# Install dependencies
pip install -r requirements.txt

# Collect static files (optional, needed if you're using Django's staticfiles)
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate