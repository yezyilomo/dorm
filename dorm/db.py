from flask import Flask
from flaskext.mysql import MySQL
import random, collections, sha3

## Database configuration information ###################################
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = None
app.config['MYSQL_DATABASE_PASSWORD'] = None
app.config['MYSQL_DATABASE_DB'] = None
app.config['MYSQL_DATABASE_HOST'] = None
mysql.init_app(app)
#########################################################################
db__name__=None
db__tables__=[]


def execute(sql_statement):
     """This is a method for executing sql statements given as argument
     """
     conn=mysql.connect()
     cursor=conn.cursor()
     cursor.execute(sql_statement)
     conn.commit()
     records=cursor.fetchall()
     conn.close()
     cursor.close()
     return records

def functions_maker(name):
     """This is a method used to return objects of class table, it allow users to
        access database table through it's name
     """
     def new_function():
       return table(name)
     return new_function

def configure(**data):
      """This is a method for configuring a database to be used,
         It generally accept three specified arguments which are
         db_user, db_password, db_name and db_host, it's called as
         db.configure( db_user='your_value',db_name='your_value',db_host='your_value',db_password='your_value' )
         in 'database/config.py' file
      """
      app.config['MYSQL_DATABASE_USER'] = data['db_user']
      app.config['MYSQL_DATABASE_PASSWORD'] = data['db_password']
      app.config['MYSQL_DATABASE_DB'] = data['db_name']
      app.config['MYSQL_DATABASE_HOST'] = data['db_host']
      global db__name__
      db__name__ =  data['db_name']
      all_tables=execute("show tables")
      global db__tables__
      for table_name in all_tables:
         globals().update({ table_name[0] : functions_maker(table_name[0]) })
         db__tables__.append(table_name[0])

def hash(string):
     """This is a method which is used to hash information(eg passwords) for
        privacy purpose, it uses sha3 to hash and add some characters to the
        hashed string for increasing security
     """
     hashed=sha3.sha3_512(string).hexdigest().decode("utf-8")
     additional_security="^dorm@ilo@yezy^#$%!flaskapp^"
     return hashed+additional_security

def drop_tb_with_foreign_key_check(table):
      """This is a method which is used in droping database tables with the argument
         as a table name to be dropped
      """
      sql_statement="drop table "+table
      execute(sql_statement)

def drop_tb_without_foreign_key_check(table):
      """This is a method which is used in droping database tables with the argument
         as a table name to be dropped
      """
      sql_statement="SET FOREIGN_KEY_CHECKS = 0; drop table if exists "+ table +" ; SET FOREIGN_KEY_CHECKS = 1;"
      execute(sql_statement)

def truncate_tb_with_foreign_key_check(table):
      """This is a method which is used in truncating database tables with the argument
         as a table name to be truncated
      """
      sql_statement="truncate table "+ table
      execute(sql_statement)

def truncate_tb_without_foreign_key_check(table):
      """This is a method which is used in truncating database tables with the argument
         as a table name to be truncated
      """
      sql_statement="SET FOREIGN_KEY_CHECKS = 0; truncate table "+ table+ " ; SET FOREIGN_KEY_CHECKS = 1;"
      execute(sql_statement)

def create_db(db_name):
      """This is a method which is used to create database with the argument
         as database name to be created
      """
      sql_statement="create database "+db_name
      execute(sql_statement)

def drop_db(db_name):
      """This is a method which is used in droping database with the argument
         as database name to be dropped
      """
      sql_statement="drop database "+db_name
      execute(sql_statement)

def get_objects(raw_records, table):
      """This is the actual method which convert records extracted form a
         database into objects, it generally create those objects from class
         record and assign them attributes corresponding to columns and their
         values as extracted from the database, It returns a normal tuple
         containing record objects
      """
      record_objects_list=[]
      for record in raw_records:
         ob=record_objects(table)
         for col, value in zip(ob.table__columns__.keys(), record):
            setattr(ob,str(col),str(value))
         record_objects_list.append(ob)
      return tuple(record_objects_list)

def get_query_condition(data):
      """This method format a condition to be used in db query
         during database update, it generally return a formated
         string with a condition to be used after where clause in
         db query
      """
      st=""
      for key in data:
           if isinstance(data[key],str):
              st=st+" "+key+"='"+str(data[key])+"',"
           else:
              st=st+" "+key+"="+str(data[key])+","
      return str(st[:len(st)-1])

def random_table():
      """This is not necessary, it's just a method which select a table name
         randomly from a list of tables in a database used and return it as
         string
      """
      sql_statement="show tables"
      all_tables=execute(sql_statement)
      rd=random.randint(0,len(all_tables)-1)
      return all_tables[rd][0]

class field(object):
   """This is a class used to define database fields and their constrains
   """
   def __init__(self,**data):
      self.model=""
      self.ref_field=""
      self.field={"key":None,'sql_statement': "field__name "+data['type'] }
      if len(data)==2 and 'constrain' in data:
         self.field['sql_statement']+=" "+data['constrain']
      elif len(data)==2 and 'key' in data:
         self.field['key']=data['key']
      elif len(data)==3 and 'constrain' in data and 'key' in data:
         self.field['sql_statement']+=" "+data['constrain']
         self.field['key']=data['key']
      elif len(data)==3 and 'key' in data and 'ref' in data:
         self.field['key']=data['key']
         reference=data['ref'].split('.')
         self.model=reference[0]
         self.ref_field=reference[1]
      elif len(data)==4 and 'key' in data and 'ref' in data and 'constrain' in data:
         self.field['sql_statement']+=" "+data['constrain']
         self.field['key']=data['key']
         reference=data['ref'].split('.')
         self.model=reference[0]
         self.ref_field=reference[1]
      else:
         pass

class arranged_attrs(type):
    def __new__(cls, name, bases, attrs):
        clss=type.__new__(cls,name, bases,attrs)
        clss.all__fields__=attrs
        return clss

    @classmethod
    def __prepare__(mcls, cls, bases):
        return collections.OrderedDict()

class model(object, metaclass=arranged_attrs):
   """This is a class which is used to define raw database, it's inherited by all
      classes used in creating database tables
   """
   def create(self):
     """This is a method used to create database tables
     """
     create_statement="create table "+str(self.__class__.__name__)+"("
     sql_statement=""
     primary_key=""
     foreign_key=""
     for fld in self.all__fields__:
       field_val=self.all__fields__[fld]
       if isinstance(field_val, field):
          sql_statement=sql_statement+field_val.field['sql_statement'].replace('field__name',fld)+" ,"
          if field_val.field['key']=='primary':
             primary_key+=fld+" ,"
          if field_val.field['key']=='foreign':
             foreign_key+=', FOREIGN KEY ('+fld+') REFERENCES ' +field_val.model+ ' ('+ field_val.ref_field +')'
     primary_key='PRIMARY KEY('+primary_key[:len(primary_key)-1]+")"
     create_statement=create_statement+sql_statement+primary_key+foreign_key+")"
     execute(create_statement)

class table(object):
   """This is a class for defining a database table as object
   """
   def __init__(self,table_name):
     """This is a constructor method which takes table name as
        argument and create an object from it
     """
     self.table__name__=table_name
     all_cols=execute("show columns from "+str(self.table__name__))
     self.table__columns__=collections.OrderedDict()
     for col_name in all_cols:
        self.table__columns__.update({str(col_name[0]): str(col_name[1])})
     keys=execute("show index from "+str(self.table__name__)+" where Key_name='PRIMARY'")
     self.primary__keys__=collections.OrderedDict()
     for key in keys:
        self.primary__keys__.update({str(key[4]): str(self.table__columns__[key[4]])})

   def get(self, col='no_column'):
         """This is a method which returns all records from a database as
            a custom tuple of objects of record
         """
         raw_records=execute("select * from "+str(self.table__name__))
         if col != 'no_column':
           return custom_tuple_read(get_objects(raw_records,self)).get(col)
         return custom_tuple_write(get_objects(raw_records,self))

   def find(self,**pri_key_with_val):
        """This is a method for finding a single specific record by using it's
           primary key(s), here the argument to this method is the dict which
           contains primary key(s) and it's/their corresponding value(s), the
           format of argument is  { primary_key1: value1, primary_key2: value2, ...}
        """
        condition=get_query_condition(pri_key_with_val)
        record=self.where(condition)
        if len(record)>1:
          raise Exception("You hava passed non-primary key argument(s)")
        elif len(record)==0:
          return None
        else:
          return record[0]

   def where(self,*data):
         """This is a method which is used to query and return records from a
            database as a custom tuple of objects of record, the criteria used
            to query records is specified as argument(s), This method accept two
            forms of arguments, the first form is three specified arguments which
            form a query condition eg  where("age", ">", 20),
            and the second form is a single argument which specify a query condition
            eg in the first example we could obtain the same result by using
            where("age > 20")
         """
         sql_statement=""
         if len(data)==3:
            col,expr,val=data[0],data[1],data[2]
            if isinstance(val, list):
               val=tuple(val)
            if isinstance(val,str):
              sql_statement=''.join(["select * from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ","'",val,"'"])
            else:
              sql_statement=''.join(["select * from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ",str(val)])
         elif len(data)==1 :
            cond=data[0]
            sql_statement=''.join(["select * from ",str(self.table__name__)," where ",cond])
         else:
            raise Exception("Invalid agruments")
         raw_records=execute(sql_statement)
         return custom_tuple_write( get_objects(raw_records,self) )

   def columns_to_insert(self,data):
      """This is a method which format colums as string to be used in insert
         query
      """
      st="("
      for col in data:
            st=st+col+","
      st=st[:len(st)-1]+")"
      return st

   def values_to_insert(self,data):
      """This is a method which format values as string to be used in insert
         query
      """
      st="("
      if isinstance(data, dict):
          for val in data:
             if "char" in self.table__columns__[val] or "text" in self.table__columns__[val] or "date" in self.table__columns__[val] or "time" in self.table__columns__[val]:
                st=st+"'"+data[val]+"',"
             else :
                st=st+str(data[val])+","
      elif isinstance(data, tuple):
          i=0
          for val in data:
             col_type=list(self.table__columns__.values())[i]
             if "char" in col_type or "text" in col_type or "date" in col_type or "time" in col_type:
                st=st+"'"+val+"',"
             else :
                st=st+str(val)+","
             i=i+1
      st=st[:len(st)-1]+")"
      return st

   def insert(self,*values,**data):
      """This is a method which is used to insert records into a database, with
         specified arguments as colums and their corresponding values to insert
         into a database, It generally return a record which has been inserted
         into your database
      """
      if len(values)==0 and len(data) > 0:
         sql_statement="insert into "+ str(self.table__name__) +" "+self.columns_to_insert(data)+ " values "+self.values_to_insert(data)
      elif  len(data)==0 and len(values) == len(self.table__columns__):
         sql_statement="insert into "+ str(self.table__name__) + " values "+self.values_to_insert(values)
      else:
         raise Exception("Invalid arguments to 'insert' function")
      execute(sql_statement)
      pri_key_with_val=collections.OrderedDict()
      if len(values)==0 and len(data) > 0:
           for prk in self.primary__keys__:
              pri_key_with_val.update({prk:data[prk]})
      else:
          for prk in self.primary__keys__:
             position=list(self.table__columns__.keys()).index(prk)
             pri_key_with_val.update({prk:values[position]})

      return self.find(**pri_key_with_val)

   def join(self,table2,join_type='inner'):
     """This is a method which is used in joining database tables with first
        arguments as table to join to, and second argument as join type which
        is inner by default
     """
     table1=self
     table2=table(table2)
     whole_table=joined_tables(join_type,table1,table2)
     return whole_table

class joined_tables(object):
    """This is a class which defines a table formed as a result of joining two
       tables
    """
    def __init__(self,join_type, table1, table2):
      """This is a constructor which initializes a table with important parameters
      """
      self.table__name__=table1.table__name__+"_and_"+table2.table__name__
      self.tables__=[table1.table__name__,table2.table__name__]
      self.join__type__=join_type
      table1_columns=[ ( table1.table__name__+'_'+key,  table1.table__columns__[key] ) for  key  in  table1.table__columns__ ]
      table2_columns=[ ( table2.table__name__+'_'+key,  table2.table__columns__[key] ) for  key  in  table2.table__columns__ ]
      joined_table_columns=table1_columns+table2_columns
      table1_primary_keys=[ ( table1.table__name__+'_'+key,  table1.primary__keys__[key] ) for  key  in  table1.primary__keys__ ]
      table2_primary_keys=[ ( table2.table__name__+'_'+key,  table2.primary__keys__[key] ) for  key  in  table2.primary__keys__ ]
      primary_lst=table1_primary_keys+table2_primary_keys
      self.table__columns__=collections.OrderedDict(joined_table_columns)
      self.primary__keys__=collections.OrderedDict(primary_lst)

    def on(self,*data):
      """This is a method which does the actual joining and return records according
         to the conditions specified in join condition
      """
      if len(data)==3:
        col1, op, col2=data[0], data[0], data[0]
        sql_statement="SELECT * FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+ " ON " +col1+ op + col2
      elif len(data)==1:
        sql_statement="SELECT * FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+ " ON " +data[0]
      else:
        raise Exception("Invalid arguments")
      raw_records=execute(sql_statement)
      return custom_tuple_read(get_objects(raw_records,self))

    def onwhere(self,on_cond,*data):
         """This is a method which is used to query and return records from a table
            arose as a result of joining two tables, with arguments as 'ON' condition and
            'WHERE' condition
         """
         sql_statement=""
         if len(data)==3:
            col,expr,val=data[0],data[1],data[2]
            sql_statement="SELECT * FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+" on "+on_cond+ " where "+str(col)+" "+str(expr)+" "+str(val)
         elif len(data)==1:
            cond=data[0]
            sql_statement="SELECT * FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+" on "+on_cond+" where "+cond
         else:
            raise Exception("Invalid agruments")
         raw_records=execute(sql_statement)
         return custom_tuple_read(get_objects(raw_records,self))

class record_objects(object):
   """This is a class for defining records as objects,
      It generally produce objects which corresponds to
      records extracted from a database
   """
   def __init__(self, table):
      """This is a constructor which initializes record object with import parameters
         from table object which is passed as the argument to it
      """
      self.table__name__=table.table__name__
      self.table__columns__=table.table__columns__
      self.primary__keys__=table.primary__keys__

   def get_query_values(self, data):
      """This method format values to be filled to a database
         during database record insertions, it generally return
         a formated string with values to be inserted in db
      """
      st=""
      for key in data:
           val=getattr(self,str(key))
           if isinstance(data[key],str):
              st=st+" "+key+"='"+str(val)+"',"
           else:
              st=st+" "+key+"="+str(val)+","
      return str(st[:len(st)-1])

   def update(self, **data):
      """This is the actual method for updating a specific record
         in a database with arguments as columns and their corresponding
         values for the record
      """
      values=get_query_condition(data)
      condition=self.get_query_values(self.primary__keys__)
      sql_statement="update "+ str(self.table__name__)+" set "+values+" where "+ condition.replace(',',' and')
      execute(sql_statement)

   def delete(self):
      """This is the actual method for deleting a specific record
         in a database
      """
      condition=self.get_query_values(self.primary__keys__)
      sql_statement="delete from "+ str(self.table__name__)+" where "+ condition.replace(',',' and')
      execute(sql_statement)

class custom_tuple_read(tuple):
   """This is a class for converting a normal tuple to a custom tuple
      with some import methods like update, delete etc, all for different
      records manipulations
   """

   def count(self):
     """This is a method for counting records
     """
     return len(self)

   def get_all_colums(self,col_name):
     """This is a method for counting records
     """
     for record in self:
       yield getattr(record, col_name)

   def get(self,col_name):
     """This is a method for counting records
     """
     col_vals=tuple(self.get_all_colums(col_name))
     return  col_vals

   def ensure_one(self):
      """This is a method for ensuring that only one record is returned and not
         a tuple or custom_tuple of records
      """
      if len(self)==1:
        return self[0]
      else:
        raise Exception("There is more than one records")

class custom_tuple_write(custom_tuple_read):
   """This is a class for converting a normal tuple to a custom tuple
      with some import methods like update, delete etc, all for different
      records manipulations
   """
   def update(self,**data):
      """This is a method helper for updating specific records with inputs to
         the database as specified arguments
      """
      for record in self:
         record.update(**data)

   def delete(self):
      """This is a method helper for deleting specific records in a database
      """
      for record in self:
         record.delete()
