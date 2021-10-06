# digify-task
This project is a simple banking system that each user can open an account, delete it, **withdraw**, **deposit**, **transfer** money.<br><br>
![alt text](https://res.cloudinary.com/dunooqow2/image/upload/v1633461339/Datebase_ER_for_Gamification.png)
<br><br>
to see above chart just click on this [**link**](https://lucid.app/luart/63b665ca-7a4e-4606-84bb-5868a8e08e19/edit?invitationId=inv_4b06e331-d9cc-4889-9fce-b12865fd0a6d)
<br><br>
**note:** keep in mind that there is lots of constraints that was defined in models and serializer and the main code to make suer it works as expcted.
<br><br>
to run this project you need to have `docker` and `docker-compose` installed, then type below command in the terminal<br>
`docker-compose up`<br>
if you like to apply tests, then type below command<br>
`docker-compose run web sh -c "cd app && python manage.py test && flake8"`<br>
to see API documentation lookup `http://localhost:8000/swagger/` url<br>
