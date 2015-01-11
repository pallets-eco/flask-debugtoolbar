from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import Column, Integer, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

app = Flask('basic_app_plain_sqlalchemy')
app.debug = True
app.config['SECRET_KEY'] = 'abc123'

# make sure these are printable in the config panel
app.config['BYTES_VALUE'] = b'\x00'
app.config['UNICODE_VALUE'] = u'\uffff'


engine = create_engine('sqlite://')
toolbar = DebugToolbarExtension(app, sqlalchemy_engine=engine)


Base = declarative_base()
class Foo(Base):
    __tablename__ = 'foo'
    id = Column(Integer, primary_key=True)


@app.route('/')
def index():
    Base.metadata.create_all(engine)
    session = Session(engine)
    session.query(Foo).filter_by(id=1).all()
    return render_template('basic_app.html')


if __name__ == '__main__':
    app.run()