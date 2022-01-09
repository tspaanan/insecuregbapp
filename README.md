# Insecure GuestBook

Project I from [Cyber Security Base 2021](https://cybersecuritybase.mooc.fi/) organized by the University of Helsinki (in collaboration with [MOOC.fi](https://www.mooc.fi/) and [F-Secure](https://www.f-secure.com/)).

As explained in the project [description](https://cybersecuritybase.mooc.fi/module-3.1), "the participants will construct software with security flaws, point out the flaws in the project, and provide the steps to fix them."

This project—a simple GuestBook Web App—contains five security flaws from [OWASP's Top 10 Web Application Security Risks](https://owasp.org/www-project-top-ten/).

All the security flaws and the steps for their mitigation are described in the essay below.

## Installation

Clone the repository, then run both commands in a Python environment that has both django and requests packages installed ([see the course instructions for more details](https://cybersecuritybase.mooc.fi/installation-guide)) to start the web server.
```
python3 manage.py migrate
python3 manage.py runserver
```

## Project I Essay

#### General thoughts on the project:

OWASP had updated their list of [Top 10 Web Application Security Risks](https://owasp.org/www-project-top-ten/) in the summer of 2021. For this project I decided to simply take the five most prominent security risks and introduce them to the project. First, I built a small web application (a web guestbook) using the Django framework, with SQLite as the database engine. Then I introduced the flaws. Because Django is a very robust framework with no obvious security issues with its default configuration, most of the time this simply meant that I had to disable something to prevent Django from protecting my web application, or I had to come up with something arbitrary (and obviously foolish) to give room for an attack to succeed. Only with security risk #4 in the OWASP list (Insecure Design) did I feel that I could truly come up with something original (albeit not very wise) to open the design of my web application for attack.

#### FLAW 1: A01:2021-Broken Access Control
https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/confused_user_management.py#L7

Broken Access Control refers to situations, in which access is granted to resources even though it should not be. Here, a convoluted management of user data in both Django's built-in auth_user table in the database and another table (insecuregbapp_visitor) leads to an oversight as data needs to be duplicated and moved around: all users who register are accidentally granted full admin rights, and have access to the hidden admin panel at /admin just with their user credentials.

At the root of the problem lies a [poorly chosen default value](https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/models.py#L6), that is propagated through the application (as such, this flaw is also an example of Security Misconfiguration).

The immediate fix for this flaw is to change the default value to 0. However, the core problem here is the introduction of a feature (Visitor-model) that duplicates functionality already in Django framework. To avoid further mishaps, a total refactoring of Visitor-model functionality to use Django's built-in user management system instead is in order.

#### FLAW 2: A02:2021-Cryptographic Failures
https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/views.py#L42

Cryptographic Failures takes the mantle of what was previouly known as Sensitive Data Exposure, as the first is practically always the cause of the latter. Here, instead of using Django's robust cryptographic properties, I have written [my own module for hashing passwords](https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/poor_crypto.py), which I then misuse by applying it twice (for good measure!), in both directions. It is a substitution cipher. The end result is that the user password is now written into the database as clear-text (that is, without encryption).

(There are other cryptographic failures in the project, as well: the application traffic is plain http, for starters, even though sensitive information such as passwords are transferred; Django's cryptographic key for the project is also present in the public remote repository, at https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/projekti1/settings.py#L23)

There is almost never any reasons to try and write one's own cryptographic algorithms: to fix this flaw, Django's built-in capabilities, which use PBKDF2 algorithm with a SHA256 hash, should be used instead.

#### FLAW 3: A03:2021-Injection
https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/views.py#L67

Injection places hostile data in the database. Here, I have opened the doors for XSS-vulnerability with two actions. First, I have shunned Django's object-relational mapping (ORM) handling, and decided to write directly into the database without sanitizing user input. Second, I have disabled XSS-protections from my html-template with |safe -option (https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/templates/insecuregbapp/index.html#L23).

Consequently, since none of the special characters are escaped any more, any JavaScript a user writes into the text field in index.html—say,
```
<script>alert("hacked");</script>
```
—will now be run for every page user, for every page load.

To fix this flaw, any of the following would suffice: remove |safe -option from template; parameterize user input when doing raw SQL queries, for example, using %s for substitution (without quotation marks around it!); use Django's ORM-system instead of circumventing it.

#### FLAW 4: A04:2021-Insecure Design
https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/insecuregbapp/views.py#L19

This newly introduced category refers to security flaws at the architectural level. These flaws are introduced at a low level, so even a robust framework cannot shield the developer from their effects. Here, I am inputting the username into the page itself (into a hidden input-field). I will then use this inputted username to identify the sender, when they send their message. Consequently, it is trivial to impersonate any registered user, especially as the message is send via GET-request: simply craft the proper parameters.

For example, the following GET-request writes the message 'hacked again!' into the guestbook as if it were sent by someone registered as 'user5' (assuming the server is waiting requests at localhost:8000, and there really is a registered user by that username in the database):
```
http://localhost:8000/insecuregbapp/addmessage?newmessage=hacked+again%21&insecure_username=user5
```
As such, this flaw is also an example of Identification and Authentication Failures. The core problem is that there is no authentication of the user when it matters: at the moment they are sending data that need to be processed. User credentials should be checked at that point (Django's request.user can be used to see who is currently signed in). This would obviously also remove the need to input the username into the page template.

(Also, POST-request should be used for sending data instead of GET-request)

#### FLAW 5: A05:2021-Security Misconfiguration
https://github.com/tspaanan/insecuregbapp/blob/a82c137fe4ed2b9bba4c712178cc06ed3f84259c/projekti1/settings.py#L26

According to OWASP, some 90% of applications include some form of misconfiguration. The worst setting in Django to misconfigure is certainly to leave debug-mode on. To do that is to introduce yet another issue of Broken Access Control, as any error situations end up revealing practically all the inner functionality of the web application, even if its source code were not publicly available.

Let's follow some of the steps that would disclose how to impersonate the user as in Flaw #4 simply by following the overly helpful error messages. Any malformed request—say, to /insecure—would first reveal the existence of the hidden admin-panel. Following the other hint by the error message, another malformed request under /insecuregbapp—say, to /insecuregbapp/nothing—would then reveal all the paths the web application is configured to listen to. Further GET-request to /insecuregbapp/addmessage would then tell that the application is waiting for some object called 'Visitor' ("Visitor matching query does not exist.").

Code snippet provided by Django's debug-mode would the reveal that a GET-parameter named 'insecure_username' is expected. Providing some other visitor's username as parameter would now divulge that something is to be written into the database to the 'content'-column, and that something is clearly a string ("can only concatenate str (not "NoneType") to str"). Further search through the web interface reveals that index.html has a text field named 'newmessage'. Trying out that for a parameter, and we have just learned how to exploit Flaw #4, just by following hints given by the error messages (and a little bit of poking around).

To fix this particular security misconfiguration, change the value of DEBUG to False.
