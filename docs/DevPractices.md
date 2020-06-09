# Development Practices
This document serves to inform on the Project Management and Technical Development frameworks used in the project.

## Project Management
Software Development is a complex topic that has many models and frameworks. Thankfully for Orbital and our Mentor, the development team had a chance to learn about the many practices used in Software Engineering.
This section will explain the methodologies and frameworks used in project management.
### Scrum (Agile Model)
![Scrum](/docs/images/Scrum.png)<br>
[Scrum](https://en.wikipedia.org/wiki/Scrum_(software_development)) is a framework used under the [Agile software development model](https://en.wikipedia.org/wiki/Agile_software_development), 
and the general process can be explained in the diagram above. It serves to break a team's work into goals that can be achieved within a certain time frame.
For our project, Orbital is already designed to have three one-month long periods between each Milestone submission. 
With only 2 members in the team and just 3 months to complete the project, there needs to be an adjustment to the framework to for our needs. 
This includes having both members as part of the Development Team, with 1 member taking the role of the Product Manager, and the other taking the role of the Scrum Master.

### Kanban Boards
![Kanban](/docs/images/Kanban.png)<br>
Unsurprisingly, GitHub is used as the host for version control with Git, so its features should be used to a great extent in terms of the software engineering aspect of the project.
[Kanban boards](https://en.wikipedia.org/wiki/Kanban_board) are a feature used under the Projects section of each GitHub repository, and are extremely useful in providing an overview of the work at various stages of the project.

### UML Diagrams
For most people, reading long lines of text to explain a concept can be downright impossible without any diagrams. 
This project also then uses [UML Diagrams](https://en.wikipedia.org/wiki/Unified_Modeling_Language) to explain the flow of the logic which can be found in abundance in the [Developer Guide](/docs/DeveloperGuide.md).
Explanations of some of the Diagrams used can also be found in the [Documentation section](/docs/DeveloperGuide.md#doc)

### Testing

## Technical Development
### Flask
[Flask](https://flask.palletsprojects.com/en/1.1.x/) is a micro and lightweight web development framework that makes use of Python to build web applications. 
Flask was chosen for development due to its ease of use, along with the developer friendly syntax of Python, a language which the development team was already familiar with.
It is known to be [configurable](https://flask.palletsprojects.com/en/1.1.x/foreword/#what-does-micro-mean).
[This tutorial made by Miguel Grinberg](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world) also proved to be extremely useful in the implementation of the various features in the platform.
It might be helpful to mention that Django - a full-stack web development framework also in Python - was also a choice, but the development team had previous experience with Flask leading to its choice over Django.

### Model View Controller (MVC)
[Model-view-controller](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller) is a software design framework for developing user interfaces, and due to its popularity, was used in the project.
Its main feature is separation of the different areas of development.
Further explanation on how it is applied in Flask can be found in the [Developer Guide](DeveloperGuide.md#arch).

### RESTful API
[REST, which stands for REpresentation State Transfer](https://en.wikipedia.org/wiki/Representational_state_transfer), is an architectural style used in defining constraints for creating web applications.
Our web application makes use of the RESTful API when making HTTP requests such as GET or POST requests. 
The team saw no reason to deviate from using the REST API to the alternative, 
[such as SOAP](https://www.upwork.com/hiring/development/soap-vs-rest-comparing-two-apis/#:~:text=REST%20is%20an%20architectural%20style.,SOAP%20APIs%20perform%20an%20operation.).