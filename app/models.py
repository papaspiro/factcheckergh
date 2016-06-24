from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import lm
from datetime import datetime
from app import app

import sys

if sys.version_info >= (3,0):
	enable_search = False
else :
	enable_search = True
	import flask.ext.whooshalchemy as whooshalchemy


@lm.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


#base model for all models to inherit from
class Base(db.Model):

	__abstract__ = True
	
	id = db.Column(db.Integer,primary_key=True)
	created_at = db.Column(db.DateTime,default=db.func.current_time_stamp())
	modified_at = db.Column(db.DateTime,default=db.func.current_time_stamp(),onupdate=db.func.current_timestamp())




class User(UserMixin,db.Model):
	id = db.Column(db.Integer(),primary_key=True)
	email = db.Column(db.String(),unique=True,index=True)
	username = db.Column(db.String(),unique=True,index=True)
	password_hash =  db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)
	role_id = db.Column(db.Integer(),db.ForeignKey('role.id'))
	avartar = db.Column(db.String())
	
	#status = db.Column(db.Integer(),db.ForeignKey('status.id')) 
	status = db.Column(db.SmallInt(),nullable=False)


	articles = db.relationship('Article', backref='author', lazy='dynamic')
	
	#status = db.relations('Status',backref='users',lazy='dynamic')

	def __init__(self , **kwargs):
		super(User,self).__init__(**kwargs)
		if self.role is None:
			if self.email == app.config['ADMIN_EMAIL']:
				self.role = Role.query.filter_by(permissions=0xff).first()
		if self.role is None:
			self.role =  Role.query.filter_by(default=True).first()	



	def can(self,permissions):
		return self.role is not None and self.permissions(
			self.permissions & permissions ) == permissions


	def is_administrator(self):
		return self.can(Permission.ADMINISTER)



	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')


	@password.setter
	def password(self,password):
		self.password_hash = generate_password_hash(password)


	def verify_password(self,password):
		return check_password_hash(self.password_hash,password)


	@property
	def is_authenticated(self):
		return True


	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False


	def get_id(self):
		try:
			return unicode(self.id)
		except:
			return str(self.id)

	def __repr__(self):
		return "User <%s>" %(self.username)


	def generate_confirmation_token(self,expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'],expiration)
		return s.dumps({'confirm':self.id})


	def confirm(self,token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False

		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		return True



class Role(Base):
	name = db.Column(db.String(64))
	#The default field should be set to True for only one role and False for all the others. 
	#The role marked as default will be the one assigned to new users upon registration.

	default = db.Column(db.Boolean,default=False,index=True)
	permissions = db.Column(db.Integer())


	users = db.relationship('User',backref='role',lazy='dynamic')




	@staticmethod
	def insert_roles():
		roles = {
			'MEMBER':(Permission.REPORT_STATEMENT | Permission.COMMENT_ON_STATEMENT,True),
			'MODERATOR': (Permission.REPORT_STATEMENT | Permission.COMMENT_ON_STATEMENT |
				Permission.MODERATE_STATEMENT ,False),
			'EDITOR': (Permission.REPORT_STATEMENT | Permission.COMMENT_ON_STATEMENT |
				Permission.MODERATE_STATEMENT ,False),
			'ADMINISTRATOR' : (0xff,False)
		}

		for r in roles :
			#check if role exists already
			role = Role.query.filter_by(name=r).first()
			if role is None: 
				 role = Role(name=r)
			role.permissions = roles[r][0]
			role.status = roles[r][1]
			db.session.add(role)	
		db.session.commit()

	def __str__(self):
		return self.name 


class Permission:
	REPORT_STATEMENT = 0x01
	COMMENT_ON_STATEMENT = 0x02
	MODERATE_STATEMENT = 0x04
	PUBLISH_STATEMENT = 0x08
	ADMINISTER =  0x80


class Organization(Base):
	name = db.Column(db.String(128),nullable=False)
	avartar = db.Column(db.String('128'),nullable=False)

	def __str__(self):
		return self.name 



class Category(Base):
    name = db.Column(db.String(50))
    description = db.Column(db.String(250))

    def __str__(self):
		return self.name 



class Veracity(Base):
	name = db.Column(db.String(128))
	description = db.Column(db.String(600))
	avartar = db.Column(db.String(128))


	def __str__(self):
		return self.name 


class Actor(Base):
	first_name = db.Column(db.String(128) nullable=False)
	middle_name = db.Column(db.String(128),nullable=True)
	last_name = db.Column(db.String(128),nullable=False)
	avartar = db.Column(db.String(128),nullable=False)
	organization_id = db.Column(db.Integer(),db.ForeignKey('organization.id'))
	

	#relationships
	claims = db.relationship('Claim',backref="actor",lazy="dynamic")
	organization = db.relationship('Organization',backref="people",uselist=False)


	def __str__(self):
		if self.name:
			return self.first_name + " " + self.middle_name +  " "  + self.last_name
		return self.first_name  +  " "	 self.last_name





class Status(db.Model):
	id = db.Column(db.Integer(),primary_key=True)
	description = db.Column(db.String())
	current = db.Column(db.Integer())
	default = db.Column(db.Boolean,default=False,index=True)

	#The default field should be set to True for only one status and False for all the others. 
	#The status marked as default will be the one assigned to new users upon registration.



class Article(Base):
	__searchable__ = ['body']
	title = db.Column(db.String(128),nullable=False)
	summary = db.Column(db.String())
	body = db.Column(db.Text())
	author_id = db.Column(db.Integer(),db.ForeignKey('user.id'))
	#avartar = db.Column(db.String())

	def __repr__(self):
		return self.body




class AnnonymousUser(AnonymousUserMixin):

	def can(self,permissions):
		return False

	def is_administrator():
		return False









if enable_search:
	whooshalchemy.whoosh_index(app,Statement) 	
	whooshalchemy.whoosh_index(app,Article)
lm.anonymous_user = AnnonymousUser







