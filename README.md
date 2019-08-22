# flask_task

Steps to configure and run the api

1)install packages using pip from requirements.txt file

2)from root folder, open cmd or terminal and run following command - python orig.py

3)now open postman to test the api

4) to register a admin user do following
    create a POST method with following url -
        127.0.0.1:5000/api/registration
        follow image 1 from images folder
        with json payload as following:
            {
                'uname': 'username',
                'passwd': 'password',
                'is_admin': 1
            }

5) to register a normal user do following
    same procedure to follow as admin user except we have to put 0 as value for 'is_admin' field in json response

6) to login for any user do following
    create a GET request with following url -
        127.0.0.1:5000/api/login
        with authorization of basic auth which is available in Authorization tab
        put the username and password accordingly
        follow image 2 from images folder
        it will return token. Copy it

7) to create a content do following
    create a POST request with following url -
        127.0.0.1:5000/api/content
        with following fields
        i) headers as image 3.1 in images folder
        ii) formdata payload as image 3.2 in images folder
        iii) we have to provide categories for content as a string as following: 'cat1, cat2, cat3, cat4' 

8) to update a content do following
    create a PUT request with following url:
    127.0.0.1:5000/api/content/<content_id>
    with same field as above step

9) to delete a content do following
    create a DELETE request with following url -
        127.0.0.1:5000/api/content/<content_id>
        with following fields
        i) headers as image 3.1 in images folder

10) to get all contents for a user do following
    create a GET request with following url: 
        127.0.0.1:5000/api/contents
        with following fields
        i) headers as image 3.1 in images folder
    It will return the data according to user type
    if user is admin then it will return all records
    if user is normal user then it will return all records created by the same user

11) to get a single content for a user do following
    create a GET request with following url: 
        127.0.0.1:5000/api/content/<content_id>
        with following fields
        i) headers as image 3.1 in images folder
    this url will only work for normal user and not for admin user

