import flask
from flask_restful import Api, Resource
import requests
import os

app = flask.Flask(__name__)
api = Api(app)
# Change template dir to root of the project
app.template_folder = os.path.abspath(os.path.dirname(__file__))
print(app.template_folder)
class check(Resource):
  def post(self):
    # Get data from request
    data = flask.request.get_json()

    if data['api_type'] == 'routinehub_api':
      # Get shortcut's data from data
      sh_data = data['sh_data']
      # Get shortcut's id from data
      sh_id = sh_data['ID']
      # Send request to RoutineHub API
      r = requests.get(f'https://routinehub.co/api/v1/shortcuts/{sh_id}/versions/latest')
      # API returns HTML page with error if there any
      # Check if response is HTML
      if r.text.find('<!DOCTYPE html>') == -1:
        pass
      else:
        # If response is HTML, return error
        return {'error': 'rh_api error: shortcut not found'}
      # Get data from response
      r = r.json()
      # Compare shortcut's version with version on RH
      sh_ver = float(sh_data['Version'])
      rh_ver = float(r['Version'])
      # If version on RH is higher than shortcut's version
      if rh_ver > sh_ver:
        s = {}

        s['embed'] = {}
        s['embed']['title'] = ('🆕 A new version is available now.'
                              ''
                              f' 	{sh_ver} ↗️ {rh_ver}')
        s['embed']['vcard'] = f'''
BEGIN:VCARD
N:Install
PHOTO;ENCODING=b:{images.vcard.install}
NICKNAME:{r.URL}
END:VCARD

BEGIN:VCARD
N:View on RoutineHub
PHOTO;ENCODING=b:{images.vcard.view}
NICKNAME:https://routinehub.co/shortcut/{sh_id}
END:VCARD

BEGIN:VCARD
N:Skip
PHOTO;ENCODING=b:{images.vcard.skip}
END:VCARD'''
        s['embed']['vcard_skip'] = 'Skip'
        return s
      elif rh_ver == sh_ver:
        return {'continue': True}
      elif rh_ver < sh_ver:
        s = {}

        s['embed'] = {}
        s['embed']['title'] = ('⚠️ A rollback is available now.'
                              ''
                              f' 	{sh_ver} ↘️ {rh_ver}')
        s['embed']['vcard'] = f'''
BEGIN:VCARD
N:Install
PHOTO;ENCODING=b:{images.vcard.install}
NICKNAME:{r.URL}
END:VCARD

BEGIN:VCARD
N:View on RoutineHub
PHOTO;ENCODING=b:{images.vcard.view}
NICKNAME:https://routinehub.co/shortcut/{sh_id}
END:VCARD

BEGIN:VCARD
N:Skip
PHOTO;ENCODING=b:{images.vcard.skip}
END:VCARD'''
        s['embed']['vcard_skip'] = 'Skip'
        return s

api.add_resource(check, '/check')

class redirect(Resource):
  def get(self):
    query = flask.request.args.get('type')
    headers = {'Content-Type': 'text/html'}
    return flask.make_response(flask.render_template('redirect.html', url=query), 200, headers)

class test(Resource):
  def get(self):
    headers = {'Content-Type': 'text/html'}
    return flask.make_response(flask.render_template('redirect.html', url='https://example.com/'), 200, headers)

api.add_resource(test, '/')

@app.route('/src/<file>')
def files(file):
  # If file is not in /src, return 404
  if not os.path.isfile(f'src/{file}'):
    return flask.make_response("404 Not Found", 404)
  # If file is in /src, return file
  return flask.send_file(app.template_folder+f'/src/{file}')
# Start server
def run():
  app.run(host='0.0.0.0', port=8080)