from flask import request, current_app, jsonify
from sqlalchemy import exc, text
from pydantic import BaseModel, ValidationError
from typing import Type

from ...models.base import Base
from ... import db
from ..common.utils.exceptions import NotFoundException, InvalidPayloadException, BadRequestException, \
    ValidationException
from ..common.utils.helpers import get_query_from_text, session_scope


class BaseAPI:
    def post(self, logged_in_user_id: int,
             validator: Type[BaseModel],
             entity: Type[Base],
             post_data: dict = None):
        """Standard POST call"""
        post_data = dict(post_data or request.get_json())
        if not post_data:
            raise InvalidPayloadException()
        try:
            with session_scope(db.session) as session:
                try:
                    data = validator(logged_in_user_id=logged_in_user_id, **post_data)
                except ValidationError as e:
                    raise ValidationException(e)

                model = entity(**data.dict())
                db.session.add(model)
                return jsonify(message=f'{entity.__tablename__} was added'), 201
        except exc.SQLAlchemyError:
            db.session.rollback()
            raise InvalidPayloadException()

    def get_by_id(self, logged_in_user_id: int,
                  id_: int,
                  entity: Type[Base],
                  json_func: str = 'json'):
        """Standard GET by Id call"""
        model = entity.get(id_)
        if not model:
            raise NotFoundException(message=f'{entity.__tablename__} does not exist')
        return jsonify(getattr(model, json_func)())

    def get(self, logged_in_user_id: int,
            entity: Type[Base],
            json_func: str = 'json',
            custom_filter=None):
        """Standard GET call"""
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', current_app.config.get('POSTS_PER_PAGE'), type=int)

        query = get_query_from_text('filter')
        order_by = get_query_from_text('order_by')

        try:
            """
            Custom filter allows us to pass additional criterion, such as to limit visibility
            An example is a normal user querying and only active entities should be returned,
            custom filter limits the result to only active entities
            """
            if custom_filter is not None:
                models = entity.query.order_by(text(order_by), entity.created_at.desc()).filter(text(query),
                                                                                                custom_filter)
            else:
                models = entity.query.order_by(text(order_by), entity.created_at.desc()).filter(text(query))

            models = models.paginate(page, per_page, False, max_per_page=current_app.config.get('MAX_PER_PAGE'))

            return jsonify({'page': models.page,
                            'per_page': models.per_page,
                            'number_of_pages': models.pages,
                            f'{entity.__tablename__}s': [getattr(model, json_func)() for model in models.items]})
        except exc.SQLAlchemyError:
            raise BadRequestException()

    def put(self, logged_in_user_id: int,
            id_: int,
            validator: Type[BaseModel],
            entity: Type[Base],
            post_data: dict = None):
        """Standard PUT call"""
        post_data = dict(post_data or request.get_json())
        if not post_data:
            raise InvalidPayloadException()
        try:
            with session_scope(db.session) as session:
                model = entity.get(id_)
                if not model:
                    raise NotFoundException(message=f'{entity.__tablename__} does not exist')
                try:
                    data = validator(logged_in_user_id=logged_in_user_id, model=model, **post_data)
                except ValidationError as e:
                    raise ValidationException(e)

                for key, value in data.dict().items():
                    if value is not None:
                        setattr(model, key, value)
                return jsonify(message=f'{entity.__tablename__} was updated')
        except exc.SQLAlchemyError:
            db.session.rollback()
            raise InvalidPayloadException()

    def delete(self, logged_in_user_id: int,
               id_: int,
               entity: Type[Base]):
        """Standard DELETE call"""
        model = entity.get(id_)
        if not model:
            raise NotFoundException(message=f'{entity.__tablename__} does not exist')
        try:
            db.session.delete(model)
            db.session.commit()
            return jsonify(message=f'{entity.__tablename__} was deleted')
        except exc.SQLAlchemyError:
            db.session.rollback()
            raise InvalidPayloadException()

    def delete_with_validation(self, logged_in_user_id: int,
                               id_: int,
                               validator: Type[BaseModel],
                               entity: Type[Base]):
        """Standard DELETE call with validation, useful for endpoints where deletion is based on some restriction"""
        try:
            with session_scope(db.session) as session:
                model = entity.get(id_)
                if not model:
                    raise NotFoundException(message=f'{entity.__tablename__} does not exist')
                try:
                    validator(logged_in_user_id=logged_in_user_id, model=model)
                except ValidationError as e:
                    raise ValidationException(e)
                db.session.delete(model)
                return jsonify(message=f'{entity.__tablename__} was deleted')
        except exc.SQLAlchemyError:
            db.session.rollback()
            raise InvalidPayloadException()