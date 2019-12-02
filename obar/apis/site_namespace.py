from flask_restplus import Namespace, Resource, fields
from flask import request
from .marshal.fields import site_fields, site_fields_post
from obar.models import db, Site
from sqlalchemy.exc import OperationalError, IntegrityError
from werkzeug.exceptions import InternalServerError, Conflict, NotFound

authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

site_ns = Namespace('site', description='Site related operations', authorizations=authorizations)

site_model = site_ns.model('Site', site_fields)
site_model_post = site_ns.model('Site Post', site_fields_post)


@site_ns.route('')
class SitesAPI(Resource):

    @site_ns.doc('get_sites')
    @site_ns.response(200, 'Return a list of products')
    @site_ns.response(500, 'Internal server error')
    @site_ns.marshal_list_with(site_model)
    def get(self):
        """
        Get the list of sites
        """
        try:
            sites = Site.query.all()
        except OperationalError:
            raise InternalServerError(description='Site table does not exists.')
        return sites, 200

    @site_ns.doc('post_site')
    @site_ns.response(201, 'Resource created')
    @site_ns.response(500, 'Internal server error')
    @site_ns.response(409, 'Resource already exists')
    @site_ns.expect(site_model_post)
    def post(self):
        """
        Creates a new Site
        """
        site = Site(site_address=request.json['address'])
        db.session.add(site)
        try:
            db.session.commit()
        except OperationalError:
            raise InternalServerError(description='Site table does not exists')
        except IntegrityError:
            raise Conflict(description=site.__repr__() + ' already exists')
        return {'message':  'Resource created'}, 201


@site_ns.route('/<int:id>')
class SiteAPI(Resource):

    @site_ns.doc('get_site')
    @site_ns.marshal_with(site_model)
    @site_ns.response(200, 'Success')
    @site_ns.response(404, 'Resource not found')
    def get(self, id):
        """
        Get site data
        """
        site = Site.query.filter_by(site_id=id).first()
        if site is None:
            raise NotFound()
        return site, 200
