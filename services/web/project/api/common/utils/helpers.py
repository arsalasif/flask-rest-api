from contextlib import contextmanager
from datetime import datetime
from flask import current_app, request
from sqlalchemy import exc
from urllib import parse

from ....api.common.utils.exceptions import ServerErrorException, InvalidPayloadException, NotFoundException, \
    ValidationException


@contextmanager
def session_scope(session):
    """
    Provide a transactional scope around a series of operations.
    """
    try:
        yield session
        session.commit()
    except (InvalidPayloadException, NotFoundException, ValidationException) as e:
        session.rollback()
        raise e
    except exc.SQLAlchemyError:
        session.rollback()
        raise ServerErrorException()


def get_date(date: str) -> datetime:
    """
    Convert str to date in a specific format
    """
    return datetime.strptime(date, current_app.config.get('DATE_FORMAT'))


def get_date_str(date: datetime) -> str:
    """
    Convert date to str in a specific format
    """
    return date.strftime(current_app.config.get('DATE_FORMAT'))


def get_query_from_text(query: str) -> str:
    """
    Get query from text from request
    Query must have (, ) brackets, this method essentially removes the trailing brackets
    """
    query = request.args.get(query, default='', type=str)
    query = query[1:-1]
    return parse.unquote(query)


def register_api(blueprint, view, endpoint, url, pk='id', pk_type='int'):
    """
    Register CRUD endpoints for API
    """
    view_func = view.as_view(endpoint)
    blueprint.add_url_rule(url, defaults={pk: None},
                           view_func=view_func, methods=['GET', ])
    blueprint.add_url_rule(url, view_func=view_func, methods=['POST', ])
    blueprint.add_url_rule(f'{url}<{pk_type}:{pk}>', view_func=view_func,
                           methods=['GET', 'PUT', 'DELETE'])
