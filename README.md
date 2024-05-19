# PDF Translator

INT-2008 final project
### Thành viên
- Nguyễn Hoàng Vũ
- Nguyễn Đức Anh
- Lê Tuấn Anh

- Link Demo: https://drive.google.com/file/d/1MFC88zhkR9ftI_wu_TUpmThqTBdHKXhE/view?fbclid=IwZXh0bgNhZW0CMTAAAR1PjR1IlARhqglqvFHX5RpNuChHcU55dY7nmJ8hmkTXP-06Sc3nz2hemkY_aem_AUOzM4bBkfXduy0hDU4hx4U1J_M5tAnNDGoImjPkSJKhJ-1RKNdEkHYFhRFBVA9LrHKsBkh9jWLp24V_q0SUVlBU
- Link Báo cáo: https://docs.google.com/document/d/1n2iBfOnevw4AwQ0Db6yu2tAbqWQGsZ40/edit?usp=sharing&ouid=108325216285804048496&rtpof=true&sd=true

- Link model : https://drive.google.com/drive/folders/13lYPPAkNqCDgQldid83cPpRfAe-yzANX?usp=sharing

  
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Website dịch văn bản file tài liệu tiếng Anh sang tiếng Việt.

## Cách chạy dự án
- Copy 2 file trong phần <a href='https://drive.google.com/drive/folders/13lYPPAkNqCDgQldid83cPpRfAe-yzANX?usp=sharing'> model</a>  vào thư mục
  <a href='https://github.com/thepluck/pdf_translator/tree/master/pdf_translator/static'>static </a>

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
- Nguyễn Văn A là một sinh viên học CNNT thường xuyên phải tiếp xúc sử dụng các tài liệu giáo trình bằng tiếng Anh. Là một người có nền tảng tiếng Anh chưa vững vì vậy A liên tục gặp khó khăn với việc sử dụng tiếng Anh. Mặc dù có nhiều mô hình dịch như google tuy nhiên gặp vấn đề trong một số ngữ cảnh dịch không đúng với văn phong người Việt và Các tài liệu PDF được dịch tuy nhiên không đúng với định dạng mong muốn. Vì vậy A mong muốn web site có khả năng dịch đúng với ngữ cảnh của tiếng Việt hơn đồng thời file PDF có định dạng chính xác hơn.
### Architecture
- Sử dụng công nghệ Cookiecutter Django cung cấp template cho một ứng dụng Django hoàn chỉnh.
https://cookiecutter-django.readthedocs.io/en/latest/index.html
- Tích hợp sẵn các công nghệ hiện đại vào ứng dụng như:
+ Docker trong việc đóng gói sảm phẩm triển khai và quản lý môi trường.
+ Sử dụng PostgetSQL làm cơ sở dữ liệu.
- Tích hợp sẵn giao diện người dùng và các chức năng xác thực người dùng như đăng ký, đăng nhập
- Sử dụng mô hình pre-train được cung cấp sẵn trên huggingface do vinAI cung cấp.
- Sử dụng EasyOrc để trích xuất văn bản.
- MarkRCNN để phân tích hình ảnh.
