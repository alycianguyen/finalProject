import webapp2
import jinja2
import os
import logging
import time
import urllib2
import json
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import users
import mimetypes

#set up environment for Jinja
#this sets jinja's relative directory to match the directory name(dirname) of
#the current __file__, in this case, main.py
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# CLASSES TO INSTANTIATE OBJECTS
class Comment(ndb.Model):
    name = ndb.StringProperty()
    message = ndb.StringProperty()
    message_code = ndb.StringProperty()

class Code(ndb.Model):
    code = ndb.StringProperty()

# CLASSES TO INSTANTIATE IMAGES
class UserImages(ndb.Model):
    user = ndb.StringProperty()
    file_name = ndb.StringProperty()
    blob = ndb.BlobProperty()
    message_code = ndb.StringProperty()

# CLASSES TO INSTANTIATE POLLS
class Entries(ndb.Model):
    activities = ndb.StringProperty()
    count = ndb.IntegerProperty()
    name2 = ndb.StringProperty()



class MainHandler(webapp2.RequestHandler):
    def get(self):
        custom_page = self.request.get('code')
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render())
        query_code = self.request.get('code')

class Custom(webapp2.RequestHandler):
    def get(self):
        my_vars = {
            "code1": self.request.get('code1'),
            "newCode": self.request.get('newCode'),
            "name": self.request.get('name'),
            "message": self.request.get('message')
            }
        code1 = self.request.get('code1')
        name = None
        message = None
        name_and_messages = []
        for comments in Comment.query(Comment.message_code==code1).fetch():
            name_and_messages.append({"name":comments.name, "message":comments.message})

        #Alycia's main.py
        image_names = []
        query = UserImages.query(UserImages.message_code==code1)
        results = query.fetch()
        for name in results:
            image_names.append(name.file_name)

        template = jinja_environment.get_template('templates/custom.html')
        self.response.out.write(template.render(my_vars, name=name, name_and_messages=name_and_messages, images = image_names,))

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
        logging.info("trial 1")

        if name and message:
            comment = Comment(name=name, message=message, message_code=message_code)
            comment.put()
            time.sleep(1)

        name_and_messages = []
        for comments in Comment.query(Comment.message_code==code1).fetch():
            name_and_messages.append({"name":comments.name, "message":comments.message})

        #Alycia's main.py
        image_names = []
        query = UserImages.query(UserImages.message_code==code1)
        results = query.fetch()
        for name in results:
            image_names.append(name.file_name)

        #Phung's main.py
        get_name = self.request.get("name2")

        activities = self.request.get("activities")
        activities_list = activities.split(',')

        get_entries = Entries.query(Entries.name2==get_name).fetch()
        list_get_entries = {}
        for i in get_entries:
            list_get_entries[i.activities] = i.count
            logging.info(list_get_entries)

        voting_activity_list =[]
        for activities in activities_list:
            if activities not in list_get_entries:
                count=0
                entries = Entries(activities=activities, name2=get_name, count=count)
                entries.put()
            else:
                count = list_get_entries[activities]
            voting_activity_list.append({"activities":activities, "count":count})



        template = jinja_environment.get_template('templates/custom.html')
        self.response.out.write(template.render(my_vars, name=name, name_and_messages=name_and_messages, images = image_names, activities_list=voting_activity_list, name2=get_name))




#Alycia's Classes
class FileUpload(webapp2.RequestHandler):
    def post(self):
        message_code = self.request.get('code1')
        code1 = self.request.get('code1')
        file_upload = self.request.POST.get("file", None)
        file_name = file_upload.filename
        image = UserImages(user=self.request.get('username'), file_name=file_name, blob=file_upload.file.read(), message_code=message_code)
        image.put()
        time.sleep(1)

        self.redirect('/custom?code1='+ code1 +'#contact', True)

class ImageHandler(webapp2.RequestHandler):
    def get(self):
        pic_file = self.request.get("name")
        query = UserImages.query(UserImages.file_name == pic_file)
        result = query.get()

        self.response.headers[b'Content-Type'] = mimetypes.guess_type(result.file_name)[0]
        self.response.write(result.blob)

#Phung's Classes
class SubmitHandler(webapp2.RequestHandler):
    def post(self):
        get_name = self.request.get("get_name")
        choice = self.request.arguments()
    #    logging.info(choice)
        if choice[0] == "get_name":
            actual_activity = choice[1]
        else:
            actual_activity=choice[0]

        activity = Entries.query(Entries.activities==actual_activity).get()
        if choice:
            activity.count += 1
        activity.put()
        allEntries = Entries.query(Entries.name2==get_name).order(-Entries.count).fetch()

        data = [i.to_dict() for i in allEntries]
        main_template = env.get_template('votes.html')
        self.response.out.write(main_template.render({'activities': data}))

class CountUpdate(webapp2.RequestHandler):
    def post(self):
        activity_name = self.request.get('activity_name')
        logging.info("this is the activity name" + activity_name)
        updated_activity = Entries.query(Entries.activities==activity_name).get()
        logging.info("THIS IS THE LIST")
        logging.info(updated_activity)
        single_activity_votes = updated_activity.count + 1
        updated_activity.count = single_activity_votes
        updated_activity.put()
        updated_counts = {'count':updated_activity.count}

        self.response.out.write(updated_activity.count)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/custom', Custom),
    ('/file_upload', FileUpload),
    ('/images', ImageHandler),
    ('/vote', SubmitHandler),
    ('/count', CountUpdate)

], debug=True)
