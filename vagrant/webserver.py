from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body><h1>Restaurants</h1>"
                for restaurant in session.query(Restaurant).order_by(Restaurant.id):
                    message += "Restaurant Name: " + restaurant.name + "</br>"
                    message += "<a href = \"#\"> Edit </a> </br>"
                    message += "<a href = \"#\"> Delete </a> </br>"
                    message += "</br></br></br>"
                message += "</body></html>"
                self.wfile.write(message)
                return

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = ""
                message += "<html><body><h1>Restaurants</h1>"
                message += "<h2> Enter new restaurant </h2>"
                message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                message += "<h2>What is the Restaurant Called?</h2>"
                message += "<input name='name' type='text' placeholder='New Restaurant Name' >"
                message += "<input type='submit' value='Create'> </form>"
                message += "</body></html>"
                self.wfile.write(message)
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


    def do_POST(self):
            try:
                if self.path.endswith("/restaurants/new"):
                    ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                    if ctype == 'multipart/form-data':
                        fields = cgi.parse_multipart(self.rfile, pdict)
                        messagecontent = fields.get('name')

                    # Create new Restaurant Object
                    newRestaurant = Restaurant(name=messagecontent[0])
                    session.add(newRestaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            except:
                pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
