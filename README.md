# digify-task
This project is a simple banking system that each user can open an account, delete it, **withdraw**, **deposit**, **transfer** money.<br><br>
to run this project you need to have `docker` and `docker-compose` installed, then type below command in the terminal<br>
`docker-compose up`<br>
if you like to apply tests first type below command<br>
`docker-compose run web sh -c "cd app && python manage.py test && flake8"`<br>
