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
- Với vai trò là học sinh tôi muốn một trang web có khả năng dịch tài liệu vì tôi gặp khó khăn với tiếng Anh.
### Personas
- Nguyễn Văn A là một sinh viên học CNNT thường xuyên phải tiếp xúc sử dụng các tài liệu giáo trình bằng tiếng Anh. Là một người có nền tảng tiếng Anh chưa vững vì vậy A liên tục gặp khó khăn với việc sử dụng tiếng Anh, do có nhiều loại mô hình dịch tuy nhiên mỗi cái áp dụng cho một ngữ cảnh trường hợp khác nhau. Vì vậy 1 trang web có tính năng cho phép dịch tài liệu bằng nhiều mô hình khác nhau được A quan tâm đến và sử dụng để dịch những tài liệu khác nhau.

### Architecture
- Sử dụng công nghệ Cookiecutter Django cung cấp template cho một ứng dụng Django hoàn chỉnh. 
https://cookiecutter-django.readthedocs.io/en/latest/index.html
- Tích hợp sẵn các công nghệ hiện đại vào ứng dụng như:
+ Docker trong việc đóng gói sảm phẩm triển khai và quản lý môi trường.
+ Sử dụng PostgetSQL làm cơ sở dữ liệu.
+ Sử dụng Celery giúp xử lý các tác vụ không đồng bộ.
+ Sử dụng Redis cho caching và message broker.
- Tích hợp sẵn giao diện người dùng và các chức năng xác thực người dùng như đăng ký, đăng nhập
- Sử dụng các mô hình pre-train được cung cấp sẵn trên huggingface do vinAI,vietAI cung cấp và thư viện googletrans của google.
