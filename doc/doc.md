## Directory of this Repository  

RC_web  
├── doc  
├── LICENSE  
├── manage.py  
├── RC_web  
│   ├── __init__.py  
│   ├── settings.py  
│   ├── urls.py  
│   └── wsgi.py  
├── README.md  
├── templates  
│   └── web  
│       ├── images  
│       │   ├── loading.gif  
│       │   └── shape.png  
│       ├── index.html  
│       └── process.html  
└── web  
    ├── admin.py  
    ├── apps.py  
    ├── __init__.py  
    ├── migrations  
    │   └── __init__.py  
    ├── models.py  
    ├── rcdata.py  
    ├── rcmain.py  
    ├── tests.py  
    ├── urls.py  
    └── views.py  

### /RC_web  

Settings of Django, serving as a bond between wsgi and this application.

### /templates  

Frontend templates, including html files and images.  

In the future, they will be replaced by better ones.

### /web  

Main sources of this application.  

views.py, the view function, reponses the request of users.  

rcdata.py pre-sets the classes of data type of the reinforced concrete.  

rcmain.py calculates all.  

