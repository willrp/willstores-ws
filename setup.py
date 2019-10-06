from setuptools import setup

setup(
   name="willstores-ws",
   version="0.0.1",
   description="Willstores Web service for WillBuyer demonstration platform.",
   license="MIT",
   author="Will Roger Pereira",
   author_email="willrogerpereira@hotmail.com",
   url="https://github.com/willrp/willstores-ws",
   install_requires=[
       "elasticsearch-dsl<6.0.0,>=5.0.0",
       "Flask",
       "flask-restplus",
       "marshmallow",
       "python-dotenv",
       "requests",
       "Werkzeug"
   ],
)
