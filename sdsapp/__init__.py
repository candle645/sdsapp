from pyramid.config import Configurator

from sdsapp.model.database import XMLDBAdapter
from sdsapp.model.category import Category
from sdsapp.model.article import Article
from sdsapp.xslt import XSLTTransform

from sdsapp.handlers.category import CategoryHandler
from sdsapp.handlers.article import ArticleHandler
from sdsapp.handlers.access import AccessHandlerSingleton

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
#    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route ('home', '/')
    config.add_route ('category', '/catalog/{category}/items')
    config.add_route ('article_show', '/catalog/{category}/{article}')
    config.add_route ('article_edit', '/catalog/{category}/{article}/edit')
    config.add_route ('article_delete', '/catalog/{category}/{article}/delete')
    config.add_route ('article_create', '/catalog/new_article')
    config.add_route ('article_import', '/catalog/import_article')
    config.add_route ('login', '/login')
    config.add_route ('logout', '/logout')
    config.scan()
    
    # Initialize app-specific stuff, this Application-wide objects will be available by request.registry.<object> further.
    #    --- Data storage
    config.registry.SDSDatabase = XMLDBAdapter ()
    config.registry.SDSDatabase.init (dict (path = settings.get ('sdsapp.db_path')))

    #    --- Business logic
    config.registry.SDSDataHandlers = {
                                       Category.ITEM_TYPE: CategoryHandler (config.registry.SDSDatabase),
                                       Article.ITEM_TYPE: ArticleHandler (config.registry.SDSDatabase),
                                       }
    
    config.registry.SDSDataHandlers [Category.ITEM_TYPE].generate_test_categories ()
    
    #    --- Authorization/authentification and access control
    access_handler = AccessHandlerSingleton ()
    config.registry.SDSAccessHandler = access_handler
    # Everyone can see start page 
    access_handler.grant_permission ('$any$', 'top')
    # Everyone can see category, but in future we might add more actions to this view, 
    # so lets explicitly grant access only to "catalog" action for now
    access_handler.grant_permission ('$any$', 'category', 'catalog')
    # Everyone can view articles in article view
    access_handler.grant_permission ('$any$', 'article', 'show')
    # Only registered and logged-in users can create new articles
    access_handler.grant_permission ('$user$', 'article', 'create', '$new$')
    access_handler.grant_permission ('$user$', 'article', 'import')
    # Article owners can modify and/or delete their articles 
    access_handler.grant_permission ('$user$', 'article', 'modify', '$own$')
    access_handler.grant_permission ('$user$', 'article', 'delete', '$own$')
    
    # User "candle" have full access for everything 
    access_handler.grant_permission ('candle', '$any$', '$any$', '$any$')

    #    --- XSLT-based rendering
    config.registry.XSLTEngine = XSLTTransform ()
    config.registry.XSLTEngine.init (dict (path = settings.get ('sdsapp.templates_path')))
    

    # Just minimal stuff required in order to use Pyramid built-in authentication 
    # for remember/forget logged user and make it available in standard way by request.authenticated_userid
    from pyramid.authentication import AuthTktAuthenticationPolicy
    from pyramid.authorization import ACLAuthorizationPolicy
    authn_policy = AuthTktAuthenticationPolicy (
        'unused-dummy', callback=None,
        hashalg='sha512')
    config.set_authentication_policy (authn_policy)
    authz_policy = ACLAuthorizationPolicy ()
    config.set_authorization_policy (authz_policy)
    
    return config.make_wsgi_app ()
