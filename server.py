#!/usr/bin/env python

# This is a simple web server for a traffic counting application.
# It's your job to extend it by adding the backend functionality to support
# recording the traffic in a SQL database. You will also need to support
# some predefined users and access/session control. You should only
# need to extend this file. The client side code (html, javascript and css)
# is complete and does not require editing or detailed understanding.

# import the various libraries needed
import http.cookies as Cookie # some cookie handling support
# the heavy lifting of the web server
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib # some url parsing support
import base64 # some encoding support
import sqlite3
import hashlib
import numpy as np

# Run database initialiser file...
from db_initialiser import acs_db, acs_db_rtn

def build_response_refill(where, what):
    '''
    This function builds a refill action that allows part of the
    currently loaded page to be replaced.
    '''
    text = "<action>\n"
    text += "<type>refill</type>\n"
    text += "<where>"+where+"</where>\n"
    m = base64.b64encode(bytes(what, 'ascii'))
    text += "<what>"+str(m, 'ascii')+"</what>\n"
    text += "</action>\n"
    return text


def build_response_redirect(where):
    '''
    This function builds the page redirection action
    It indicates which page the client should fetch.
    If this action is used, only one instance of it should
    contained in the response and there should be no refill action.
    '''
    text = "<action>\n"
    text += "<type>redirect</type>\n"
    text += "<where>"+where+"</where>\n"
    text += "</action>\n"
    return text


def handle_validate(iuser, imagic, both=False):
    '''
    Decides if the combination of user and magic is valid
    '''
    if both == False:
        # Checking is already logged in...
        user_chk = acs_db_rtn('initial_database.db', "SELECT * FROM sessions WHERE userid=? \
                              AND active=1", (iuser,))
        if len(user_chk) == 0:
            # User not already logged in...
            return False
        # User already logged in...
        return True
    # Validating userid and magic combination...
    usermagic_chk = acs_db_rtn('initial_database.db', "SELECT * FROM sessions WHERE magic=? \
                               AND userid=? AND active=1", (imagic, iuser))
    if len(usermagic_chk) == 0:
        # User and magic combination is not valid...
        return False
    # User and magic combination is valid...
    return True


def handle_delete_session(iuser, imagic):
    '''
    Removes the combination of user and magic from the database, ending the login.
    '''
    acs_db('initial_database.db', "UPDATE sessions SET active = 0, end = CURRENT_TIMESTAMP \
           WHERE magic=? AND userid=?", (imagic, iuser))


def handle_login_request(iuser, imagic, parameters):
    '''
    A user has supplied a username (parameters['usernameinput'][0])
    and password (parameters['passwordinput'][0]) check if these are
    valid and if so, create a suitable session record in the database
    with a random magic identifier that is returned.
    Return the username, magic identifier and the response action set.
    '''
    if 'usernameinput' in parameters and 'passwordinput' in parameters:
        text = "<response>\n"
        # Search for username in database...
        chk_user = acs_db_rtn('initial_database.db', "SELECT * FROM users WHERE username=?", \
                              (parameters['usernameinput'][0],))
        if len(chk_user) == 1:
            # The user exists...
            hash_object = hashlib.sha1(parameters['passwordinput'][0].encode('utf-8'))
            hex_password = hash_object.hexdigest()
            userpass = acs_db_rtn('initial_database.db', "SELECT * FROM users WHERE username=? \
                                  AND password=?", (chk_user[0][1], hex_password))
            if len(userpass) == 1:
                # Username and password combination is valid...
                user = userpass[0][0]
                validate = handle_validate(user, imagic)
                if validate:
                    # User already logged in...
                    text += build_response_refill('message', 'User already logged in, \
                                                  please logout first.')
                    user = '!'
                    magic = ''
                    text += "</response>\n"
                    return [user, magic, text]
                # Checking magic is unique...
                while True:
                    # Assigning new magic...
                    magic = int(np.random.randint(10000000))
                    magic_chk = acs_db_rtn('initial_database.db', "SELECT * FROM sessions \
                                           WHERE magic=?", (magic,))
                    if len(magic_chk) == 0:
                        break
                # Found unique magic for user, adding new session to table...
                acs_db('initial_database.db', "INSERT INTO sessions (magic, userid) \
                       VALUES (?,?)", (magic, user))
                # Redirecting to homepage...
                text += build_response_redirect('/page.html')
            else:
                # The password is not valid...
                text += build_response_refill('message', 'Invalid password')
                user = '!'
                magic = ''
        else:
            # The user does not exist...
            text += build_response_refill('message', 'Invalid username')
            user = '!'
            magic = ''
        text += "</response>\n"
    else:
        # There was no username/password present, reporting to user...
        text = "<response>\n"
        text += build_response_refill('message', 'Error: Missing username or password.')
        user = '!'
        magic = ''
        text += "</response>\n"
    return [user, magic, text]


def handle_add_request(iuser, imagic, parameters):
    '''
    The user has requested a vehicle be added to the count
    parameters['locationinput'][0] the location to be recorded
    parameters['occupancyinput'][0] the occupant count to be recorded
    parameters['typeinput'][0] the type to be recorded
    Return the username, magic identifier (these can be empty  strings)
    and the response action set.
    '''
    text = "<response>\n"
    if 'locationinput' in parameters and 'occupancyinput' in parameters \
        and 'typeinput' in parameters:
        if handle_validate(iuser, imagic, True) != True:
            # User not logged in...
            text += build_response_refill('message', 'User not logged in, entry not added.')
            total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
            text += build_response_refill('total', str(total[0][0]))
        else:
            # Valid session, processing the entry...
            # Checking type has correct form...
            types = set(['car','bus','taxi','bicycle','motorbike','van','truck','other'])
            occups = set(['1','2','3','4'])
            if parameters['typeinput'][0] not in types:
                text += build_response_refill('message', 'Error: Incorrect vehicle type entered.')
                total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                                   WHERE include = 1 AND magic = ?", (imagic,))
                text += build_response_refill('total', str(total[0][0]))
                text += "</response>\n"
                user = iuser
                magic = imagic
                return [user, magic, text]
            # Checking occupancy has correct form...
            elif parameters['occupancyinput'][0] not in occups:
                text += build_response_refill('message', 'Error: Incorrect occupancy entered.')
                total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
                text += build_response_refill('total', str(total[0][0]))
                text += "</response>\n"
                user = iuser
                magic = imagic
                return [user, magic, text]
            # Adding entry to table...
            acs_db('initial_database.db', "INSERT INTO traffic (location, type, occupancy, \
                   magic) VALUES (?,?,?,?)", (parameters['locationinput'][0], \
                    parameters['typeinput'][0], parameters['occupancyinput'][0], imagic))
            text += build_response_refill('message', 'Entry added.')
            # Counting number of entries...
            total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
            text += build_response_refill('total', str(total[0][0]))
    else:
        # Missing one or more entry fields, reporting to user...
        text += build_response_refill('message', 'Error: One or more entry fields missing.')
        total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
        text += build_response_refill('total', str(total[0][0]))
    text += "</response>\n"
    user = iuser
    magic = imagic
    return [user, magic, text]



def handle_undo_request(iuser, imagic, parameters):
    '''
    The user has requested a vehicle be removed from the count
    This is intended to allow counters to correct errors.
    parameters['locationinput'][0] the location to be recorded
    parameters['occupancyinput'][0] the occupant count to be recorded
    parameters['typeinput'][0] the type to be recorded
    Return the username, magic identifier (these can be empty  strings)
    and the response action set.
    '''
    text = "<response>\n"
    if 'locationinput' in parameters and 'occupancyinput' in parameters \
        and 'typeinput' in parameters:
        if handle_validate(iuser, imagic, True) != True:
            # User not logged in...
            text += build_response_refill('message', 'User not logged in, \
                                          entry not removed.')
            total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
            text += build_response_refill('total', str(total[0][0]))
        else:
            # Valid session, processing the entry undo...
            # Checking type has correct form...
            types = set(['car','bus','taxi','bicycle','motorbike','van','truck','other'])
            occups = set(['1','2','3','4'])
            if parameters['typeinput'][0] not in types:
                text += build_response_refill('message', 'Error: Incorrect vehicle type entered.')
                total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                                   WHERE include = 1 AND magic = ?", (imagic,))
                text += build_response_refill('total', str(total[0][0]))
                text += "</response>\n"
                user = iuser
                magic = imagic
                return [user, magic, text]
            # Checking occupancy has correct form...
            elif parameters['occupancyinput'][0] not in occups:
                text += build_response_refill('message', 'Error: Incorrect occupancy entered.')
                total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
                text += build_response_refill('total', str(total[0][0]))
                text += "</response>\n"
                user = iuser
                magic = imagic
                return [user, magic, text]
            # Checking entry exists in table...
            exists = acs_db_rtn('initial_database.db', "SELECT * FROM traffic \
                                WHERE location=? AND type=? AND occupancy=? AND magic=? \
                                AND include = 1", (parameters['locationinput'][0], \
                                parameters['typeinput'][0], \
                                parameters['occupancyinput'][0], imagic))
            if len(exists) == 0:
                # Entry does not exist in table...
                total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                                   WHERE include = 1 AND magic = ?", (imagic,))
                text += build_response_refill('message', 'No such entry exists.')
                text += build_response_refill('total', str(total[0][0]))
            else:
                # Entry exists in table...
                # Changing entry 'include' value in table...
                acs_db('initial_database.db', "UPDATE traffic SET include = 0, \
                       removed = CURRENT_TIMESTAMP WHERE trafficid IN \
                       (SELECT trafficid FROM traffic WHERE location=? AND type=? \
                       AND occupancy=? AND magic=? AND include = 1 \
                       ORDER BY added DESC LIMIT 1)", \
                       (parameters['locationinput'][0], parameters['typeinput'][0], \
                       parameters['occupancyinput'][0], imagic))
                total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                                   WHERE include = 1 AND magic = ?", (imagic,))
                text += build_response_refill('message', 'Entry Un-done.')
                text += build_response_refill('total', str(total[0][0]))
    else:
        # Missing one or more entry fields, reporting to user...
        text += build_response_refill('message', 'Error: One or more entry fields missing.')
        total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                               WHERE include = 1 AND magic = ?", (imagic,))
        text += build_response_refill('total', str(total[0][0]))
    text += "</response>\n"
    user = iuser
    magic = imagic
    return [user, magic, text]


def handle_back_request(iuser, imagic, parameters):
    '''
    This code handles the selection of the back button on the record form (page.html)
    '''
    text = "<response>\n"
    if handle_validate(iuser, imagic, True) != True:
        text += build_response_redirect('/index.html')
    else:
        text += build_response_redirect('/summary.html')
    text += "</response>\n"
    user = iuser
    magic = imagic
    return [user, magic, text]


def handle_logout_request(iuser, imagic, parameters):
    '''
    This code handles the selection of the logout button on the summary page (summary.html)
    ************
    ************
    ****** You will need to ensure the end of the session is recorded in the database ******
    ************
    ************
    And that the session magic is revoked.
    '''
    text = "<response>\n"
    handle_delete_session(iuser, imagic)
    text += build_response_redirect('/index.html')
    user = '!'
    magic = ''
    text += "</response>\n"
    return [user, magic, text]

## This code handles a request for update to the session summary values.
## You will need to extract this information from the database.
def handle_summary_request(iuser, imagic, parameters):
    text = "<response>\n"
    if handle_validate(iuser, imagic, True) != True:
        # User not logged in, redirecting to login page...
        text += build_response_redirect('/index.html')
        user = '!'
        magic = ''
    else:
        car_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                             WHERE type='car' AND magic = ?", (imagic,))
        taxi_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                              WHERE type='taxi' AND magic = ?", (imagic,))
        bus_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                             WHERE type='bus' AND magic = ?", (imagic,))
        motorbike_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                                   WHERE type='motorbike' AND magic = ?", (imagic,))
        bicycle_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                                 WHERE type='bicycle' AND magic = ?", (imagic,))
        van_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                             WHERE type='van' AND magic = ?", (imagic,))
        truck_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                               WHERE type='truck' AND magic = ?", (imagic,))
        other_sum = acs_db_rtn('initial_database.db', "SELECT SUM(include) FROM traffic \
                               WHERE type='other' AND magic = ?", (imagic,))
        text += build_response_refill('sum_car', str(car_sum[0][0]))
        text += build_response_refill('sum_taxi', str(taxi_sum[0][0]))
        text += build_response_refill('sum_bus', str(bus_sum[0][0]))
        text += build_response_refill('sum_motorbike', str(motorbike_sum[0][0]))
        text += build_response_refill('sum_bicycle', str(bicycle_sum[0][0]))
        text += build_response_refill('sum_van', str(van_sum[0][0]))
        text += build_response_refill('sum_truck', str(truck_sum[0][0]))
        text += build_response_refill('sum_other', str(other_sum[0][0]))
        total = acs_db_rtn('initial_database.db', "SELECT COUNT(*) FROM traffic \
                           WHERE include = 1 AND magic = ?", (imagic,))
        text += build_response_refill('total', str(total[0][0]))
        text += "</response>\n"
        user = iuser
        magic = imagic
    return [user, magic, text]


# HTTPRequestHandler class
class myHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET This function responds to GET requests to the web server.
    def do_GET(self):

        # The set_cookies function adds/updates two cookies returned with a webpage.
        # These identify the user who is logged in. The first parameter identifies the user
        # and the second should be used to verify the login session.
        def set_cookies(x, user, magic):
            ucookie = Cookie.SimpleCookie()
            ucookie['u_cookie'] = user
            x.send_header("Set-Cookie", ucookie.output(header='', sep=''))
            mcookie = Cookie.SimpleCookie()
            mcookie['m_cookie'] = magic
            x.send_header("Set-Cookie", mcookie.output(header='', sep=''))

        # The get_cookies function returns the values of the user and magic
        # cookies if they exist it returns empty strings if they do not.
        def get_cookies(source):
            rcookies = Cookie.SimpleCookie(source.headers.get('Cookie'))
            user = ''
            magic = ''
            for keyc, valuec in rcookies.items():
                if keyc == 'u_cookie':
                    user = valuec.value
                if keyc == 'm_cookie':
                    magic = valuec.value
            return [user, magic]

        # Fetch the cookies that arrived with the GET request
        # The identify the user session.
        user_magic = get_cookies(self)

        print(user_magic)

        # Parse the GET request to identify the file requested and the GET parameters
        parsed_path = urllib.parse.urlparse(self.path)

        # Decided what to do based on the file requested.

        # Return a CSS (Cascading Style Sheet) file.
        # These tell the web client how the page should appear.
        if self.path.startswith('/css'):
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return a Javascript file.
        # These tell contain code that the web client can execute.
        if self.path.startswith('/js'):
            self.send_response(200)
            self.send_header('Content-type', 'text/js')
            self.end_headers()
            with open('.'+self.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # A special case of '/' means return the index.html (homepage)
        # of a website
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('./index.html', 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # Return html pages.
        elif parsed_path.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('.'+parsed_path.path, 'rb') as file:
                self.wfile.write(file.read())
            file.close()

        # The special file 'action' is not a real file, it indicates an action
        # we wish the server to execute.
        elif parsed_path.path == '/action':
            self.send_response(200) #respond that this is a valid page request
            # extract the parameters from the GET request.
            # These are passed to the handlers.
            parameters = urllib.parse.parse_qs(parsed_path.query)

            if 'command' in parameters:
                # check if one of the parameters was 'command'
                # If it is, identify which command
                # and call the appropriate handler function.
                if parameters['command'][0] == 'login':
                    [user, magic, text] = handle_login_request(user_magic[0], \
                                                               user_magic[1], parameters)
                    #The result to a login attempt will be to set
                    #the cookies to identify the session.
                    set_cookies(self, user, magic)
                elif parameters['command'][0] == 'add':
                    [user, magic, text] = handle_add_request(user_magic[0], \
                                                             user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'undo':
                    [user, magic, text] = handle_undo_request(user_magic[0], \
                                                              user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'back':
                    [user, magic, text] = handle_back_request(user_magic[0], \
                                                              user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'summary':
                    [user, magic, text] = handle_summary_request(user_magic[0], \
                                                                 user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                elif parameters['command'][0] == 'logout':
                    [user, magic, text] = handle_logout_request(user_magic[0], \
                                                                user_magic[1], parameters)
                    if user == '!': # Check if we've been tasked with discarding the cookies.
                        set_cookies(self, '', '')
                else:
                    # The command was not recognised, report that to the user.
                    text = "<response>\n"
                    text += build_response_refill('message', \
                                                  'Internal Error: Command not recognised.')
                    text += "</response>\n"

            else:
                # There was no command present, report that to the user.
                text = "<response>\n"
                text += build_response_refill('message', \
                                              'Internal Error: Command not found.')
                text += "</response>\n"
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            self.wfile.write(bytes(text, 'utf-8'))
        else:
            # A file that does n't fit one of the patterns above was requested.
            self.send_response(404)
            self.end_headers()
        return

# This is the entry point function to this code.
def run():
    print('starting server...')
    ## You can add any extra start up code here
    # Server settings
    # Choose port 8081 over port 80, which is normally used for a http server
    server_address = ('127.0.0.1', 8081)
    httpd = HTTPServer(server_address, myHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever() # This function will not return till the server is aborted.

run()
