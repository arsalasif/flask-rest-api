from .core import auth_core_blueprint
from .social import auth_social_blueprint
from .email_verification import email_verification_blueprint

"""
Add your auth blueprints here
"""
auth_blueprints = [auth_core_blueprint,
                   auth_social_blueprint,
                   email_verification_blueprint]
