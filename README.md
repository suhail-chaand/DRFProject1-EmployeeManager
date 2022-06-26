<h1>Django REST Project: Employee Manager App</h1>

<h2>Dependency installations:</h2>
<ul>
<li>django</li>
<li>djangorestframework</li>
<li>djangorestframework-simplejwt</li>
<li>django-environ</li>
<li>django-cors-headers</li>
</ul>

<h2>API endpoints:</h2>
<ul>
<li>'create_superuser/' : Create a super user</li>
<li>'create_manager/' : Create a manager</li>
<li>'create_employee/' : Manager can create an employee</li>

<li>'login/' : User login</li>
<li>'logout/' : User logout</li>

<li>'users_list/' : Super user can get list of all users</li>
<li>'employees/' : Manager can get list of all employees</li>

<li>'employee/id' : Manager can get, update or destroy an employee's details, </li>

<li>'forgot_password/id' : Request new user login password through email</li>
<li>'reset_password/id' : Change user login password</li>
</ul>