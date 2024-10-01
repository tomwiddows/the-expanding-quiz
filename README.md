# The Expanding Quiz

![screenshot](assets/images/amiresponsive.png)!

## Website Goals

### Customer Goals

- Easily access a database of randomised quiz questions
- Test knowledge with friends and/or family
- Input own questions to expand database and encourage other users
- Navigate site easily and intuitively, with instructions to follow where needed

### Business Goals

- Create a mutable database of quiz questions
- Create a community of quizzers that can mentally challenge one another
- Display questions one at a time within a web application
- Allow users to input their own questions and answers
- Allow users to remove their own questions and answers
- Allow users to flag any incorrecly uploaded questions and/or answers
- Regulate quiz questions as administrator by checking validity of questions and answers

## User Experience

### Potential Users

- Groups of friends/family that want to do a quiz for fun
- People training for a quiz
- People that want to join an online group of quizzers

### User Stories

__New User__

- I want to know what the site is about
- I want the site navigation to be intuitive and quick
- I want to have fun
- I want to upload my own questions for other people to view

__Returning User__

- I want to be able to upload more questions
- I want to view my uploaded questions
- I want to be able to edit or delete my questions and answers
- I want to know if others disagree with my answer
- I want to know if an administrator has removed my question

__Site Administrator__

- The page should be easily manageable
- The code should be well commented
- The code should contain safeguards to prevent the user from breaking the game intentionally or unintiaonally
- I should have overriding power for deleting questions/changing answers if appropriate

## Wireframes

<img src="./assets/images/index-wireframe.jpg" height="300px">  <img src="./assets/images/profile-wireframe.jpg" height="300px">

## Features

__Question__



| Feature | Page | Screenshot | Notes |
| --- | --- | --- | --- |
| Question & Answer | index.html | ![screenshot](assets/images/Q-and-A.png)! | Uses flask and jinjia templates to retrieve question_info from run.py which has already chosen a raondom question upon page load. Answer card doesn't reveal answer until arrow is clicked |
| Next Question Button | index.html | ![screenshot](assets/images/next-question-button.png) | Links to index route decorator, reloading the page with a new question. Previous question's id was stored in SHOWN_QUESTION_IDS constant so will not be shown again. |
| Login & Register Pages | login.html, register.html | ![screenshot](assets/images/register-form.png) ![screenshot](assets/images/login-form.png) | Both forms are styled identically. Each page has a button linking to the other page. Placeholders and icons increase ease of accessibility |
|  Profile & Logout | profile.html | ![screenshot](assets/images/profile-and-logout.png) | Profile name displayed using jinja templating. Logout button links to /logout route decorator. Styled identically to Login/Register buttons |
| Add a Question | profile.html | ![screenshot](assets/images/add-question-form.png) | Similar form to login and register forms. Links to /add_quesiton route decorator |
| Edit/delete Questions | profile.html | ![screenshot](assets/images/edit-or-delete.png) | Buttons link to edit/delete modal popup where forms are filled in and the database is updated. |

## Deployment

This project is deployed to Heroku. It is set to automatically update within heroku upon being pushed to GitHub. The steps to Deployment are as follows:

1. A requirements.txt file is needed for Heroku to run the app. This file contains a list of python dependencies for the project. The following command was entered to the terminal to create the requirements.txt file filled with the dependencies:

    pip freeze --local > requirements.txt

2. Heroku also requires a Procfile to run the app. This contains the start command (which app  should be run and how to run it) and is created using the following command:

    echo web: python run.py > Procfile

3. Ensure these files are pushed to GitHub

4. Go to Heroku and log in. Do so with a GitHub account to make deployment easier. 

5. Now create a new app and give it an appropriate name. The name of this app in Heroku is          'the-expanding-quiz'. Heroku also needs to know which region you are closest to. 

6. Within the 'Deploy' tab in the Heroku app, select GitHub as the deployment method. You will then 
be prompted to connect to GitHub, which is done by checking that the correct profile is displayed and copying in your GitHub repository name. Click connect. 

7. Next, go to the 'Settings' tab and click 'Reveal Config Vars'. Heroku needs to know five 
environment variables to run the app: IP, PORT, SECRET_KEY, MONGO_URI and MONGO_DBNAME. These are contained within the env.py file. Each of them should be in the format:

    os.environ.setdefault("KEY", "VALUE")

    Type these into the input boxes labelled 'KEY' and their respective values in the 'VALUE' boxes. 

    The IP should be set to 0.0.0.0 to accept all IP addresses. Add your PORT and SECRET_KEY. 

    The MONGO_URI is found within MongoDB Atlas. Once in the 'database' tab, click connect and select the 'Drivers' option under 'Connect to your application' A terminal command will be provided depending on which version of python you are using, followed by a connection string. You must add your user password (found within 'Database Access') and cluster name (in 'database') to the string where stated.

    The NONGO_DBNAME is the name of your database within the cluster.

8. Go back to the 'Deploy' tab in Heroku and 'Enable Automatic Deployment".

9. Finally, click "Deploy Branch". The app code should now begin to load within Heroku and once loaded, any changes pushed to GitHub should automatically deploy to Heroku.

## Future Features

I Want to add a Flag Questions/Answers feature, where users who are displayed a question can flag it. This means that the person who uploaded that question, as well as any administrators (myself) would be alerted that there is an issue with the question. There would be two options for flagging a question; either the answer may be wrong, or the question is inappropriate (maybe it is not a question, maybe it is offensive). If a user believes the answer is wrong, They can suggest a correction and if this correction cets a certain number of upvotes, it would replace the original answer. If a question gets flat a lot of times for being inappropriate, it would get deleted. 

## Acknowledgements

https://stackoverflow.com/questions/39299063/change-the-navbar-color-in-materializecss
https://realpython.com/python-constants/
https://www.geeksforgeeks.org/python-mongodb-find_one_and_replace-query/
https://rakeshjain-devops.medium.com/fix-to-tip-of-your-current-branch-is-behind-its-remote-counterpart-git-error-eb75f719c2d5#:~:text=%E2%80%9Cthe%20tip%20of%20your%20current,usually%20some%20sort%20of%20rebase).
https://www.geeksforgeeks.org/python-mongodb-find_one_and_replace-query/
https://fontawesome.com/
https://materializecss.com/cards.html
https://learn.codeinstitute.net/courses/course-v1:CodeInstitute+NRDB_L5+2/courseware/9e2f12f5584e48acb3c29e9b0d7cc4fe/054c3813e82e4195b5a4d8cd8a99ebaa/

Thank you to my mentor Sheryl for supporting me over slack, my totor Kaynat for our Monday stand-up meetings and my friend Sam for testing my project upon deployment