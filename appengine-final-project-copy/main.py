import webapp2
import jinja2
import os
import logging
from google.appengine.ext import ndb

#set up environment for Jinja
#this sets jinja's relative directory to match the directory name(dirname) of
#the current __file__, in this case, main.py
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class Comment(ndb.Model):
    name = ndb.StringProperty()
    message = ndb.StringProperty()
    message_code = ndb.StringProperty()

class Code(ndb.Model):
    code = ndb.StringProperty()



class MainHandler(webapp2.RequestHandler):
    def get(self):
        custom_page = self.request.get('code')
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())

    def post(self):
        my_vars = {
            "code1": self.request.get('code1'),
            "newCode": self.request.get('newCode'),
            "name": self.request.get('name'),
            "message": self.request.get('message')
            }
        name = self.request.get('name')
        message = self.request.get('message')
        message_code = self.request.get('code1')
        code1 = self.request.get('code1')

        if name and message:
            comment = Comment(name=name, message=message, message_code=message_code)
            comment.put()
            logging.info('just made a comment')
            logging.info('HELLO')


        name_and_messages = []
        for comments in Comment.query(Comment.message_code==code1).fetch():
            name_and_messages.append({"name":comments.name, "message":comments.message})

        template = jinja_environment.get_template('templates/custom.html')
        self.response.out.write(template.render(my_vars, name=name, name_and_messages=name_and_messages))




app = webapp2.WSGIApplication([
    ('/', MainHandler)

], debug=True)
