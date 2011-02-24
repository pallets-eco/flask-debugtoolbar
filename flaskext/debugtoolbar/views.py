import hashlib

import simplejson
from flask import Module, request, current_app, abort
from flaskext.sqlalchemy import SQLAlchemy
from flaskext.debugtoolbar.utils import format_sql


module = Module(__name__)



@module.route('/sql_select', methods=['GET', 'POST'])
def sql_select(render):
    statement = request.args['sql']
    params = request.args['params']

    # Validate hash
    hash = hashlib.sha1(
        current_app.config['SECRET_KEY'] + statement + params).hexdigest()
    if hash != request.args['hash']:
        return abort(406)

    # Make sure it is a select statement
    if not statement.lower().strip().startswith('select'):
        return abort(406)

    params = simplejson.loads(params)

    db = SQLAlchemy(current_app)

    result = db.engine.execute(statement, params)
    return render('panels/sqlalchemy_select.html', {
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })

@module.route('/sql_explain', methods=['GET', 'POST'])
def sql_explain(render):
    statement = request.args['sql']
    params = request.args['params']

    # Validate hash
    hash = hashlib.sha1(
        current_app.config['SECRET_KEY'] + statement + params).hexdigest()
    if hash != request.args['hash']:
        return abort(406)

    # Make sure it is a select statement
    if not statement.lower().strip().startswith('select'):
        return abort(406)

    params = simplejson.loads(params)

    db = SQLAlchemy(current_app)
    if db.engine.driver == 'pysqlite':
        query = 'EXPLAIN QUERY PLAN %s' % statement
    else:
        query = 'EXPLAIN %s' % statement

    result = db.engine.execute(query, params)
    return render('panels/sqlalchemy_explain.html', {
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })
