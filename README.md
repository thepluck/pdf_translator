# PDF Translator

INT-2008 final project
Nguyễn Hoàng Vũ 
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Dự án website dịch văn bản tài liệu sử dụng nhiều mô hình khác nhau

## Cách chạy dự án

## Các lệnh chạy ứng dụng trên local

### Yêu cầu cài đặt Docker trên máy tính.

- Chạy lệnh sau để build các image.

      $ docker compose -f local.yml build

  câu lệch này chạy lần đầu có thể tốn nhiều thời gian tuy nhiên chỉ chạy 1 lần duy nhất.

- Tiếp theo khởi chạy các container câu lệch nay được chạy mỗi khi cần chạy ứng dụng.

      $ docker compose -f local.yml up
  
- Khởi tạo dữ liệu cho trang web : lệnh này cũng chỉ chạy 1 lần hoặc khi có sự thay đổi nào liên quan đến dữ liệu.
  
      $ docker compose -f local.yml run --rm django python manage.py migrate

- Tạo tài khoản admin

      $ docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
 
- Mở trình duyệt và truy cập vào địa chỉ  http://127.0.0.1:8000/ hoặc http://127.0.0.1:8000/admin để truy cập vào trang admin
### Docker

See detailed [cookiecutter-django Docker documentation](http://cookiecutter-django.readthedocs.io/en/latest/deployment-with-docker.html).

### User story

### Personas

### Architecture
