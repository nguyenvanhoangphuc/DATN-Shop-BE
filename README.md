# trong manage.py có sử dụng dòng trên, nếu set mặc định là dev thì sẽ chạy trên môi trường dev còn nếu set là prod thì sẽ chạy trên môi trường prod
env = os.getenv("DJANGO_ENV", "dev")

