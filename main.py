import json
import os
import lib.cloudstorage
from google.appengine.api import app_identity
import webapp2
# from tilifier import Tilifier


TILESET_URI_TEMPLATE = 'tilesets/{}'

class TilesetHandler(webapp2.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        filename = data.pop('filename', None)
        if not texture_id:
            abort(404)
        # download texture by uri
        bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        texture = '/' + bucket_name + '/textures/' + filename
        tileset = '/' + bucket_name + '/tilesets/' + filename
        with cloudstorage.open(texture) as texture_file:
            with cloudstorage.open(tileset, 'w', content_type='image/png') as tileset_file:
                # TODO:
        # tilify texture to tileset
        # tilifier = Tilifier()
        # tilifier.tilify(**data)
        # upload tileset
        tileset_uri = TILESET_URI_TEMPLATE.format(texture_uri)
        # blob = bucket.blob(tileset_uri)
        # blob.upload_from_filename(tileset_uri)
        # return uri to tileset
        self.response.write('tilesets/' + filename + '\n')



app = webapp2.WSGIApplication([
    webapp2.Route('/tilesets', methods=['POST'], name='create_tileset', handler=TilesetHandler),
], debug=True)
