# Development Practices
This document serves to inform on the Project Management and Technical Development frameworks used in the project.
### Table of Contents
[1. Project Management](#project)<br>
&nbsp; &nbsp; [1.1. Scrum (Agile Model)](#scrum)<br>
&nbsp; &nbsp; [1.2. Kanban Boards](#kanban)<br>
&nbsp; &nbsp; [1.3. UML Diagrams](#uml)<br>
&nbsp; &nbsp; [1.4. Testing](#testing)<br>
[2. Technical Development](#tech)<br>
&nbsp; &nbsp; [2.1. Flask](#flask)<br>
&nbsp; &nbsp; [2.2. Model View Controller (MVC)](#mvc)<br>
&nbsp; &nbsp; [2.3. RESTful API](#rest)<br>

## 1. Project Management <a name="project">
Software Development is a complex topic that has many models and frameworks. Thankfully for Orbital and our Mentor, the development team had a chance to learn about the many practices used in Software Engineering.
This section will explain the methodologies and frameworks used in project management.
### 1.1 Scrum (Agile Model) <a name="scrum">
![Scrum](/docs/images/Scrum.png)<br>
[Scrum](https://en.wikipedia.org/wiki/Scrum_(software_development)) is a framework used under the [Agile software development model](https://en.wikipedia.org/wiki/Agile_software_development), 
and the general process can be explained in the diagram above. It serves to break a team's work into goals that can be achieved within a certain time frame.
For our project, Orbital is already designed to have three one-month long periods between each Milestone submission. 
With only 2 members in the team and just 3 months to complete the project, there needs to be an adjustment to the framework to for our needs. 
This includes having both members as part of the Development Team, with 1 member taking the role of the Product Manager, and the other taking the role of the Scrum Master.
For our documentation, User Guides represent guidance on Business Requirements, while the Developer Guide represents guidance on the Product Development aspect of the project.

### 1.2 Kanban Boards <a name="kanban">
![Kanban](/docs/images/Kanban.png)<br>
Unsurprisingly, GitHub is used as the host for version control with Git, so its features should be used to a great extent in terms of the software engineering aspect of the project.
[Kanban boards](https://en.wikipedia.org/wiki/Kanban_board) are a feature used under the Projects section of each GitHub repository, and are extremely useful in providing an overview of the work at various stages of the project.

### 1.3 UML Diagrams <a name="uml">
For most people, reading long lines of text to explain a concept can be downright impossible without any diagrams. 
This project also then uses [UML Diagrams](https://en.wikipedia.org/wiki/Unified_Modeling_Language) to explain the flow of the logic which can be found in abundance in the [Developer Guide](/docs/DeveloperGuide.md).
Explanations of some of the Diagrams used can also be found in the [Documentation section](/docs/DeveloperGuide.md#doc)

### 1.4 Testing <a name="testing">

## 2. Technical Development <a name="tech">
### 2.1 Flask <a name="flask">
[Flask](https://flask.palletsprojects.com/en/1.1.x/) is a micro and lightweight web development framework that makes use of Python to build web applications. 
Flask was chosen for development due to its ease of use, along with the developer friendly syntax of Python, a language which the development team was already familiar with.
It is known to be [configurable](https://flask.palletsprojects.com/en/1.1.x/foreword/#what-does-micro-mean).
[This tutorial made by Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) also proved to be extremely useful in the implementation of the various features in the platform.
It might be helpful to mention that Django - a full-stack web development framework also in Python - was also a choice, but the development team had previous experience with Flask leading to its choice over Django.

### 2.2 Model View Controller (MVC) <a name="mvc">
[Model-view-controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) is a software design framework for developing user interfaces, and due to its popularity, was used in the project.
Its main feature is separation of the different areas of development.
Further explanation on how it is applied in Flask can be found in the [Developer Guide](DeveloperGuide.md#arch).

### 2.3 RESTful API <a name="rest">
[REST, which stands for REpresentation State Transfer](https://en.wikipedia.org/wiki/Representational_state_transfer), is an architectural style used in defining constraints for creating web applications.
Our web application makes use of the RESTful API when making HTTP requests such as GET or POST requests.

### 2.4 Database Normalization <a name="normal">
There are multiple ways to design a database, and doing [Database Normalization](https://en.wikipedia.org/wiki/Database_normalization) can ensure that the design leads to better efficiency overall.
The database design should satisfy 3NF normalization.