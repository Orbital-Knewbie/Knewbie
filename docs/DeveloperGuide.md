# Knewbie - Developer Guide

### Table of Contents
[1. Setting up](#setup)<br>
[2. Design](#design)<br>
&nbsp; &nbsp; [2.1. Architecture](#arch)<br>
&nbsp; &nbsp; [2.2. Model component](#model)<br>
&nbsp; &nbsp; [2.3. View component](#view)<br>
&nbsp; &nbsp; [2.4. Controller component](#control)<br>
[3. Implementation](#implement)<br>
[4. Documentation](#doc)<br>
[5. Testing](#test)<br>
[6. Frequently Asked Questions (FAQ)](#faq)<br>
[User Stories](#user)<br>

## 1. Setting up <a name="setup"></a>
Refer to the guide [here](https://github.com/R-Ramana/Knewbie/blob/master/README.md).

## 2. Design <a name="design"></a>
[Flask](https://flask.palletsprojects.com/) is a micro web framework written in [Python](https://www.python.org/). This Web App makes use of the framework for its overall design.
### 2.1 Architecture <a name="arch"></a>
![Architecture Design](diagrams/Architecture.png)

The [Model-View-Controller (MVC)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) is a software design pattern that divides the program logic into the components. While some of the components may have some overlap with the others due to the nature of the Flask framework design, the Web App can still be said to consist of these three main components.
* [Model](#model): Manages data, logic and rules of application
* [View](#view): The representation to the users
* [Controller](#control): Converts input to commands for Model or View

The Web App will use the [RESTful API](https://restfulapi.net/) architectural style to perform its HTTP requests.

The *Sequence Diagram* below shows how a `POST` request for a `ContactForm` will cause the different components to interact.

{sequence-diagram}

### 2.2 Model component <a name="model"></a>
The Model component includes files:
```
├── forms.py
├── models.py
└── ...
```
![Model Class](diagrams/Model.png)
![Form Class](diagrams/Form.png)
Fig #. Structure of Model components

The Model component
* stores `User` data.
* stores `Question` data.
* defines the various `FlaskForm`s used.
* does not depend on the other components.

### 2.3 View component <a name="view"></a>
The View component includes folders (and all the files within them):
```
├── templates
    └── ...
├── content
    └── ...
└── ...
``` 
![View Component](diagrams/View.png)
The View component consists of the `HTML` templates along with `CSS` styling. 
Templates also have `Jinja` syntax, which is a templating language. 
Under the Flask framework, the `Jinja` syntax acts as part of the Controller component, changing the view logic depending on inputs from the Model component.

The View component
* Executes user commands using the Controller component
* Updates with changes to the Model data


### 2.4 Controller component <a name="control"></a>
The Controller component includes files:
```
├── views.py
├── decorator.py
├── questions.py
├── email.py
├── token.py
└── ...
```
![Controller Component](diagrams/Controller.png)
Fig #. Structure of Controller Component

The Controller component converts input from View to commands for Model and vice versa.
The files in this component consist of functions to control the logic of the application, ranging from email verification to quiz question generation. It is important to note that in Flask, there is a file specific to route the various URLs along with their HTTP methods to the right function - which in this case is `views.py`. This function can display a webpage (View component), or redirect to another function. As such, the main interaction between the View and Controller component will happen here. The other files under the Controller component would then be mainly used to interact with the Model component.

The Sequence Diagram below shows the interactions within the Controller component for the submission of the `ContactForm`.

{sequence-diagram}

## 3. Implementation <a name="implement"></a>
This section describes some noteworthy details on how certain features are implemented.
### 3.1 Progress Report
### 3.2 Classes
### 3.3 Quizzes

## 4. Documentation <a name="doc"></a>

## 5. Testing <a name="test"></a>

## 6. Frequently Asked Questions (FAQ) <a name="faq"></a>

## User Stories <a name="user"></a>
* As a {target user}, I can {feature} so that {aim of the project}.

* As a new student using the application, I can create an account so that I can log in and access the features of the application.

* As an existing educator using the application, I can update students enrolled in my class so I can track their progress in the application.

* As a student, I can log in to access tailored content as a quiz which caters to my learning abilities, and join classes which my educator creates.

* As a student, I can change my password or unique ID if required in the event either has been compromised.

* As an educator, I can log in to access classes and additional questions I have created for my students.

* As an educator, I can change my password if required in the even it has been compromised.

* As an educator, I can delete my classes, or remove participants from the classes I have created.

* As a parent, I can access the progress report to monitor my child's progress through the unique ID.'