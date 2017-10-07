from flask import Flask
from flaskext.mysql import MySQL
import random
import collections
import sha3
import copy

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


def _execute(sql_statement):
     """This is a method for executing sql statements given as string argument
        This is for internal use only
     """
     connection=mysql.connect()
     cursor=connection.cursor()
     cursor.execute(sql_statement)
     connection.commit()
     cursor.close()
     connection.close()
     if cursor.description is None:
         return None
     else:
         class empty(object):
              pass
         columns=tuple( [column[0] for column in cursor.description] )
         obj=empty()
         obj.columns=columns
         obj.fetch=cursor.fetchall()
         return obj

def execute(sql_statement): ##This method is for further modification, currently it does the same thing as _execute(sql_statement)
     """This is a method for executing sql statements given as string argument
        This is meant for external use
     """
     result= _execute(sql_statement)
     return result

def functions_maker(name):
     """This is a method used to return objects of class table, it allow users to
        access database tables through their names
     """
     def new_function():
       return actual_table(name)
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
      all_tables=_execute("show tables").fetch
      global db__tables__
      for table_name in all_tables:
         globals().update({ table_name[0] : functions_maker(table_name[0]) })
         db__tables__.append(table_name[0])

def hash(string):
     """This is a method which is used to hash information(eg passwords) for
        security purpose, it uses sha3 algorithm to hash, and  it adds some characters
        to hashed string for increasing security
     """
     hashed=sha3.sha3_512(string).hexdigest().decode("utf-8")
     additional_security="^dorm@ilo@yezy^#$%!flaskapp^"
     return hashed+additional_security

def drop_tb_with_foreign_key_check(table):
      """This is a method which is used in droping database tables with argument
         as a table name to be dropped
      """
      sql_statement="drop table "+table
      _execute(sql_statement)

def drop_tb_without_foreign_key_check(table):
      """This is a method which is used in droping database tables with argument
         as a table name to be dropped
      """
      sql_statement="SET FOREIGN_KEY_CHECKS = 0; drop table if exists "+ table +" ; SET FOREIGN_KEY_CHECKS = 1;"
      _execute(sql_statement)

def truncate_tb_with_foreign_key_check(table):
      """This is a method which is used in truncating database tables with argument
         as a table name to be truncated
      """
      sql_statement="truncate table "+ table
      _execute(sql_statement)

def truncate_tb_without_foreign_key_check(table):
      """This is a method which is used in truncating database tables with argument
         as a table name to be truncated
      """
      sql_statement="SET FOREIGN_KEY_CHECKS = 0; truncate table "+ table+ " ; SET FOREIGN_KEY_CHECKS = 1;"
      _execute(sql_statement)

def create_db(db_name):
      """This is a method which is used to create database with argument
         as a database name to be created
      """
      sql_statement="create database "+db_name
      _execute(sql_statement)

def drop_db(db_name):
      """This is a method which is used in droping database with argument
         as database name to be dropped
      """
      sql_statement="drop database "+db_name
      _execute(sql_statement)

def get_objects(raw_records, columns, table):
      """This is the actual method which convert records extracted from a
         database into record objects, it generally create those objects from class
         record and assign them attributes corresponding to columns and their
         values as extracted from a database, It returns a normal tuple
         containing record objects
      """
      columns=list(columns)
      for column in table.table__columns__:    ##check if there are colums with the same name
           splitted_column=column.split('.')
           if '.' in column and len( splitted_column )>1:
                columns[ columns.index( splitted_column[1] ) ]=column

      record_objects_list=[]
      for record in raw_records:
         rec_object=record_objects(table)
         for col, value in zip(columns, record):
            if "." in col:  ## if the column is in form of table.column make it accessible by using the same format( table.column )##########
               splitted_col=col.split('.')
               setattr( rec_object, str(splitted_col[0]), type('name', (object, ), {splitted_col[1]: value}) )  #############################
            setattr( rec_object, str(col), value )
         record_objects_list.append( rec_object )
      return tuple(record_objects_list)

def get_query_condition(data):
      """This method format a condition to be used in db query during database
         update and lookup, it generally returns a formated string with a condition
         to be used after where clause in a db query
      """
      list_of_strings=[]
      for key in data:
           if isinstance(data[key],str):
              list_of_strings.append( key+"='"+str(data[key])+"'" )
           else:
              list_of_strings.append( key+"="+str(data[key]) )
      formated_str=", ".join(list_of_strings)
      return formated_str

def random_table():
      """This is not necessary, it's just a method which select a table name
         randomly from a list of tables in a database used and return it as
         string
      """
      sql_statement="show tables"
      all_tables=_execute(sql_statement).fetch
      rd=random.randint(0,len(all_tables)-1)
      return all_tables[rd][0]

class field(object):
   """This is a class used to define table fields and their constrains
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
    """This is a metaclass intended to arrange model attributes the way they were
       defined
    """
    def __new__(cls, name, bases, attrs):
        class_=type.__new__(cls,name, bases,attrs)
        class_.all__fields__=attrs
        return class_

    @classmethod
    def __prepare__(mcls, cls, bases):
        """This is a method which arrange model attributes as they were defined
        """
        return collections.OrderedDict()

class model(object, metaclass=arranged_attrs):
   """This is a class which is used to define raw database(schema), it's inherited
      by all classes used in creating database tables
   """
   def create(self):
     """This is a method used to create database table(s)
     """
     create_statement="create table "+str(self.__class__.__name__)+"("
     sql_statement=""
     primary_key=""
     foreign_key=""
     for table_field in self.all__fields__:
          field_value=self.all__fields__[table_field]
          if isinstance(field_value, field):
             sql_statement=sql_statement+field_value.field['sql_statement'].replace('field__name',table_field)+" ,"
             if field_value.field['key']=='primary':
                 primary_key+=table_field+" ,"
             if field_value.field['key']=='foreign':
                 foreign_key+=', FOREIGN KEY ('+table_field+') REFERENCES ' +field_value.model+ ' ('+ field_value.ref_field +')'
     primary_key='PRIMARY KEY('+primary_key[:len(primary_key)-1]+")"
     create_statement=create_statement+sql_statement+primary_key+foreign_key+")"
     _execute(create_statement)

class partial_table(object):
   """This is a class for defining partial table as object, it's the result of
      using select statement, which tends to eliminate some columns and produce
      a partial table
   """
   def __init__(self,table, *columns, **kwargs):
          """This is a constructor method which takes table name as
             argument and create table object from it
          """
          self.table__name__=table.table__name__
          self.table__columns__=table.table__columns__
          self.selected__columns__=table.selected__columns__
          self.primary__keys__=table.primary__keys__
          self.table__type__="partial"
          columns_to_remove=[]
          columns_arrangement=[]
          calculated_columns=[]

          if len(columns)==1 and isinstance( columns[0], (tuple,list) ) :
               columns=tuple(columns[0])

          if 'all_except' in kwargs.keys() and ( isinstance(kwargs['all_except'], tuple) or isinstance( kwargs['all_except'], list) ):
               columns_to_remove=list(kwargs['all_except'])
               del kwargs['all_except']
               for col in columns_to_remove:
                    self.table__columns__.remove(col)
               columns_arrangement =self.table__columns__ + list(kwargs.keys())
               calculated_columns=self.table__columns__
          elif  len(columns)==1 and columns[0]=="*":
                ##leave selected tables as they were in actual table
               return
          else:
               columns_arrangement=list(columns)+list(kwargs.keys())
          self.table__columns__=columns_arrangement
          for column in kwargs:
                 calculated_columns.append( kwargs[column]+" as "+column )

          temp_list=[", ".join(columns), ", ".join(calculated_columns)]
          if temp_list[0]!="" and temp_list[1]!="" :
               self.selected__columns__=", ".join(temp_list)
          elif temp_list[0]!="" and temp_list[1]=="" :
               self.selected__columns__=temp_list[0]
          elif temp_list[0]=="" and temp_list[1]!="" :
               self.selected__columns__=temp_list[1]
          else:
               raise Exception("Invalid arguments")

   def get(self, col=None):
         """This is a method which returns all records from a database as
            a custom tuple of objects of record when no argument is passed,
            but it returns a tuple of values of a specified column passed
            as a string argument(column name)
         """
         raw_records=_execute("select " +self.selected__columns__+ " from "+str(self.table__name__))
         if col is not None:
              return custom_tuple_read(get_objects(raw_records.fetch, raw_records.columns ,self)).get(col)
         return custom_tuple_write(get_objects(raw_records.fetch, raw_records.columns,self))

   def getdistinct(self,col_name):
     """This is a method for extracting distinct values in a specified column,
        it takes string argument as column name from which values are
        suppossed to be extracted
     """
     return tuple(set(self.get(col_name)))

   def find(self,**pri_key_with_val):
        """This is a method for finding a single specific record by using it's
           primary key(s), here the argument to this method is the dict which
           contains primary key(s) and it's/their corresponding value(s), the
           format of argument is  { primary_key1: value1, primary_key2: value2, ...}
        """
        primary_keys=pri_key_with_val.keys()
        if set(pri_key_with_val) != set(self.primary__keys__):    #if user provide a non-primary key argument
            raise Exception("You hava passed non-primary key as argument(s)")

        list_of_strings=[]
        for key in pri_key_with_val:
            if isinstance(pri_key_with_val[key],str):
               list_of_strings.append( key+"='"+str(pri_key_with_val[key])+"'" )
            else:
               list_of_strings.append( key+"="+str(pri_key_with_val[key]) )
        condition=" and ".join(list_of_strings)
        record=self.where(condition)
        if len(record)==0:
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
              sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ","'",val,"'"])
            else:
              sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ",str(val)])
         elif len(data)==1 :
            cond=data[0]
            sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",cond])
         else:
            raise Exception("Invalid agruments")
         raw_records=_execute(sql_statement)
         return custom_tuple_write( get_objects(raw_records.fetch, raw_records.columns, self) )

class calculation_table(object):  ##this is a class for calculations, it's meant to separate calculations from normal queries
   """This is a class for defining a calculation database table as object, this
      table is only meant for calculations
   """
   def __init__(self,table, operation,column):
     """This is a constructor method which takes table name as
        argument and create table object from it
     """
     self.table__name__=table.table__name__
     self.table__type__="calculation"
     self.selected__columns__=selected__columns__=operation+"("+column+")"

   def get(self):  ## get for calculations
         """This is a method which returns all records from a database as
            a custom tuple of objects of record
         """
         raw_records=_execute("select " +self.selected__columns__+ " from "+str(self.table__name__))
         return raw_records.fetch[0][0]

   def where(self,*data):  ## where for calculations
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
              sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ","'",val,"'"])
            else:
              sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ",str(val)])
         elif len(data)==1 :
            cond=data[0]
            sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",cond])
         else:
            raise Exception("Invalid agruments")
         raw_records=_execute(sql_statement)
         return raw_records.fetch[0][0]

class actual_table(object):
   """This is a class for defining actual database table as object
   """
   def __init__(self,table_name):
     """This is a constructor method which takes table name as
        argument and create table object from it
     """
     self.table__name__=table_name
     self.selected__columns__="*"
     self.table__type__="actual"
     all_cols=_execute("show columns from "+str(self.table__name__))
     self.table__columns__=[]
     for col_name in all_cols.fetch:
        self.table__columns__.append( str(col_name[0]) )
     keys=_execute("show index from "+str(self.table__name__)+" where Key_name='PRIMARY'").fetch
     self.primary__keys__=[]
     for key in keys:
        self.primary__keys__.append( str(key[4]) )

   def select(self, *columns, **kwargs ):
          """This is a method which is used to select several columns to be included
             in SQL query, it accept a number of arguments which are column names passed
             as strings, if you want to select all columns except few columns you can pass
             all_except=['column1', 'column2', ...] as kwarg
          """

          partial_tb=partial_table(self, *columns, **kwargs) ##Here we use partial_table because not all columns are going to be included in select statement
          return partial_tb

   def max(self,column):
        calc_table=calculation_table(self,'max',column)
        return calc_table

   def min(self,column):
        calc_table=calculation_table(self,'min',column)
        return calc_table

   def sum(self,column):
        calc_table=calculation_table(self,'sum',column)
        return calc_table

   def avg(self,column):
        calc_table=calculation_table(self,'avg',column)
        return calc_table

   def count(self,column="*"):
        calc_table=calculation_table(self,'count',column)
        return calc_table

   def get(self, col='no_column'):
         """This is a method which returns all records from a database as
            a custom tuple of objects of record when no argument is passed,
            but it returns a tuple of values of a specified column passed
            as a string argument(column name)
         """
         raw_records=_execute("select " +self.selected__columns__+ " from "+str(self.table__name__))
         if self.table__type__=="calculation":
              return raw_records.fetch[0][0]
         if col != 'no_column':
              return custom_tuple_read(get_objects(raw_records.fetch, raw_records.columns ,self)).get(col)
         return custom_tuple_write(get_objects(raw_records.fetch, raw_records.columns,self))

   def getdistinct(self,col_name):
     """This is a method for extracting distinct values in a specified column,
        it takes string argument as column name from which values are
        suppossed to be extracted
     """
     return tuple(set(self.get(col_name)))

   def find(self,**pri_key_with_val):
        """This is a method for finding a single specific record by using it's
           primary key(s), here the argument to this method is the dict which
           contains primary key(s) and it's/their corresponding value(s), the
           format of argument is  { primary_key1: value1, primary_key2: value2, ...}
        """
        primary_keys=pri_key_with_val.keys()
        if set(pri_key_with_val) != set(self.primary__keys__)  :    #if user provide a non-primary key argument
            raise Exception("You hava passed non-primary key argument(s)")

        list_of_strings=[]
        for key in pri_key_with_val:
            if isinstance(pri_key_with_val[key],str):
               list_of_strings.append( key+"='"+str(pri_key_with_val[key])+"'" )
            else:
               list_of_strings.append( key+"="+str(pri_key_with_val[key]) )
        condition=" and ".join(list_of_strings)
        record=self.where(condition)
        if len(record)==0:
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
              sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ","'",val,"'"])
            else:
              sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",str(col)," ",str(expr)," ",str(val)])
         elif len(data)==1 :
            cond=data[0]
            sql_statement=''.join(["select " +self.selected__columns__+ " from ",str(self.table__name__)," where ",cond])
         else:
            raise Exception("Invalid agruments")
         raw_records=_execute(sql_statement)
         if self.table__type__=="calculation":
              return raw_records.fetch[0][0]
         return custom_tuple_write( get_objects(raw_records.fetch, raw_records.columns, self) )

   def values_to_insert(self,data):
      """This is a method which format values as string to be used in insertion
         query
      """
      st="("
      if isinstance(data, dict):
          for val in data:
             if isinstance(data[val],str):
                st=st+"'"+data[val]+"',"
             else :
                st=st+str(data[val])+","
      elif isinstance(data, tuple):
          for val in data:
             if isinstance(val,str):
                st=st+"'"+val+"',"
             else :
                st=st+str(val)+","
      st=st[:len(st)-1]+")"
      return st

   def insert(self,*values,**data):
      """This is a method which is used to insert records into a database table, with
         specified arguments as columns and their corresponding values to insert
         into a database, It generally returns a record which has been inserted
         into your database
      """
      if len(values)==0 and len(data) > 0:
         sql_statement="insert into "+ str(self.table__name__) +" ("  +", ".join(list(data))+  ") values "+self.values_to_insert(data)
      elif  len(data)==0 and len(values) == len(self.table__columns__):
         sql_statement="insert into "+ str(self.table__name__) + " values "+self.values_to_insert(values)
      else:
         raise Exception("Invalid arguments to 'insert' function")
      _execute(sql_statement)
      pri_key_with_val=collections.OrderedDict()
      if len(values)==0 and len(data) > 0:
           for prk in self.primary__keys__:
              pri_key_with_val.update({prk:data[prk]})
      else:
          for prk in self.primary__keys__:
             position=self.table__columns__.index(prk)
             pri_key_with_val.update({prk:values[position]})
      return self.find(**pri_key_with_val)

   def join(self,table2,join_type='inner'):
     """This is a method which is used in joining database tables with first
        arguments as table name to join to, and second argument as join type
        which is inner by default, it returns an instance of joined_tables,
        where different operations can be done
     """
     table1=self
     table2=actual_table(table2)
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
      self.tables__=[table1.table__name__, table2.table__name__]
      self.table__type__='partial'
      self.join__type__=join_type
      self.on__condition__=""
      self.selected__columns__="*"
      joined_table_columns=table1.table__columns__ + table2.table__columns__
      joined_table_primary_keys=table1.primary__keys__ + table2.primary__keys__

      duplicate_colums=[key for key in set(joined_table_columns) if joined_table_columns.count(key)>1] ##Identify columns with name collision and assign them full name ie table_name.column_name
      for col in duplicate_colums:
           if col in joined_table_primary_keys and joined_table_primary_keys.count(col)>1:
                joined_table_primary_keys[joined_table_primary_keys.index(col)]=table1.table__name__+'.'+col
                joined_table_primary_keys[joined_table_primary_keys.index(col)]=table1.table__name__+'.'+col
           joined_table_columns[joined_table_columns.index(col)]=table1.table__name__+'.'+col
           joined_table_columns[joined_table_columns.index(col)]=table2.table__name__+'.'+col
      self.table__columns__=joined_table_columns
      self.primary__keys__=joined_table_primary_keys

    def on(self,*data):
      """This is a method which specify on condition to be used in joining
         tables
      """
      if len(data)==3:
        col1, op, col2=data[0], data[0], data[0]
        self.on__condition__=col1+ op + col2
      elif len(data)==1:
        self.on__condition__=data[0]
      else:
        raise Exception("Invalid arguments")
      print(self.on__condition__)
      return self

    def get(self, column=None):
         """This is a method which returns all records from a database as
            a custom tuple of objects of record when no argument is passed,
            but it returns a tuple of values of a specified column passed
            as a string argument(column name)
         """
         sql_statement="SELECT " +self.selected__columns__+ " FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+" on "+self.on__condition__
         print(sql_statement)
         raw_records=_execute(sql_statement)
         if self.table__type__=="calculation":
              return raw_records.fetch[0][0]
         elif column is not None:
             rec_objects=get_objects(raw_records.fetch, raw_records.columns, self)
             return tuple( [ getattr(record, column) for record in rec_objects ] )
         return custom_tuple_read(get_objects(raw_records.fetch, raw_records.columns, self))

    def getdistinct(self,col_name):
     """This is a method for extracting distinct values in a specified column,
        it takes string argument as column name from which values are
        suppossed to be extracted
     """
     return tuple(set(self.get(col_name)))

    def where(self, *data):
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
            sql_statement="SELECT " +self.selected__columns__+ " FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+" on "+self.on__condition__+ " where "+str(col)+" "+str(expr)+" "+str(val)
         elif len(data)==1:
            cond=data[0]
            sql_statement="SELECT " +self.selected__columns__+ " FROM " +self.tables__[0]+ " " +self.join__type__+ " JOIN " +self.tables__[1]+" on "+self.on__condition__+" where "+cond
         else:
            raise Exception("Invalid agruments")
         print(sql_statement)
         raw_records=_execute(sql_statement)
         if self.table__type__=="calculation":
              return raw_records.fetch[0][0]
         return custom_tuple_read(get_objects(raw_records.fetch, raw_records.columns, self))

    def select(self, *columns, **kwargs):
          """This is a method which is used to select several columns to be included
             in SQL query, it accept a number of arguments which are column names passed
             as strings, if you want to select all columns except few columns you can pass
             all_except=['column1', 'column2', ...] as kwarg
          """
          tb_copy=copy.deepcopy(self)
          tb_copy.table__type__="partial"
          columns_to_remove=[]
          columns_arrangement=[]
          calculated_columns=[]

          if len(columns)==1 and isinstance( columns[0], (tuple,list) ) :
               columns=tuple(columns[0])

          if 'all_except' in kwargs.keys() and ( isinstance(kwargs['all_except'], tuple) or isinstance(kwargs['all_except'], list) ):
               columns_to_remove=list(kwargs['all_except'])
               del kwargs['all_except']
               for col in columns_to_remove:
                    tb_copy.table__columns__.remove(col)

               columns_arrangement=tb_copy.table__columns__+list(kwargs.keys())
               calculated_columns=tb_copy.table__columns__
          else:
               columns_arrangement=list(columns)+list(kwargs.keys())

          tb_copy.table__columns__=columns_arrangement

          for column in kwargs:
                 calculated_columns.append( kwargs[column]+" as "+column )

          temp_list=[", ".join(columns), ", ".join(calculated_columns)]
          if temp_list[0]!="" and temp_list[1]!="" :
               tb_copy.selected__columns__=", ".join(temp_list)
          elif temp_list[0]!="" and temp_list[1]=="" :
               tb_copy.selected__columns__=temp_list[0]
          elif temp_list[0]=="" and temp_list[1]!="" :
               tb_copy.selected__columns__=temp_list[1]
          else:
               raise Exception("Invalid arguments")
          return tb_copy

    def max(self,column):
        tb_copy=copy.deepcopy(self)
        tb_copy.selected__columns__='max('+column+')'
        tb_copy.table__type__="calculation"
        return tb_copy

    def min(self,column):
        tb_copy=copy.deepcopy(self)
        tb_copy.selected__columns__='min('+column+')'
        tb_copy.table__type__="calculation"
        return tb_copy

    def sum(self,column):
        tb_copy=copy.deepcopy(self)
        tb_copy.selected__columns__='sum('+column+')'
        tb_copy.table__type__="calculation"
        return tb_copy

    def avg(self,column):
        tb_copy=copy.deepcopy(self)
        tb_copy.selected__columns__='avg('+column+')'
        tb_copy.table__type__="calculation"
        return tb_copy

    def count(self,column="*"):
        tb_copy=copy.deepcopy(self)
        tb_copy.selected__columns__='count('+column+')'
        tb_copy.table__type__="calculation"
        return tb_copy

    def find(self, **pri_key_with_val):
        """This is a method for finding a single specific record by using it's
           primary key(s), here the argument to this method is the dict which
           contains primary key(s) and it's/their corresponding value(s), the
           format of argument is  { primary_key1: value1, primary_key2: value2, ...}
        """
        if len(pri_key_with_val)==0:
             raise Exception("Invalid arguments, Please pass primary key(s) for finding your record")
        primary_keys=pri_key_with_val.keys()
        if set(pri_key_with_val) != set(self.primary__keys__) :    #if user provide a non-primary key argument
            raise Exception("You hava passed non-primary key argument(s)")

        list_of_strings=[]
        for key in pri_key_with_val:
            if isinstance(pri_key_with_val[key],str):
               list_of_strings.append( key+"='"+str(pri_key_with_val[key])+"'" )
            else:
               list_of_strings.append( key+"="+str(pri_key_with_val[key]) )
        condition=" and ".join(list_of_strings)
        record=self.where(condition)
        if len(record)==0:
          return None
        else:
          return record[0]

class record_objects(object):
   """This is a class for defining records as objects,
      It generally produce objects which corresponds to
      records extracted from a certain database table
   """
   def __init__(self, table):
      """This is a constructor which initializes record object with import parameters
         from table object which is passed as the argument to it
      """
      self.table__name__=table.table__name__
      self.table__columns__=table.table__columns__
      self.primary__keys__=table.primary__keys__

   def get_query_values(self, data):
      """This method format string to be used as condition in finding a record
         during record deletion and update, it generally return a formated string
         with values to be inserted in a db table
      """
      list_of_strings=[]
      for column in data:
           val=getattr( self, str(column) )
           if isinstance(val,str):
              list_of_strings.append( column+"='"+str(val)+"'" )
           else:
              list_of_strings.append( column+"="+str(val) )
      formated_str=" and ".join( list_of_strings )
      return formated_str

   def update(self, **data):
      """This is the actual method for updating a specific record in a database
         with arguments as column names and their corresponding values for the
         record
      """
      values=get_query_condition(data)
      condition=self.get_query_values(self.primary__keys__)
      sql_statement="update "+ str(self.table__name__)+" set "+values+" where "+ condition
      _execute(sql_statement)

   def delete(self):
      """This is the actual method for deleting a specific record
         in a database
      """
      condition=self.get_query_values(self.primary__keys__)
      sql_statement="delete from "+ str(self.table__name__)+" where "+ condition
      _execute(sql_statement)

class custom_tuple_read(tuple):
   """This is a class for converting a normal tuple into a custom tuple
      which has some import methods like count, get etc, for record
      manipulations
   """
   def count(self):
     """This is a method for counting records
     """
     return len(self)

   def get_column_values(self,col_name):
     """This returns all values in a given column
     """
     for record in self:
       yield getattr(record, col_name)

   def get(self,col_name):
     """This is a method for extracting values in a specified column,
        it takes string argument as column name from which values are
        suppossed to be extracted
     """
     col_vals=tuple(self.get_column_values(col_name))
     return  col_vals

   def getdistinct(self,col_name):
     """This is a method for extracting distinct values in a specified column,
        it takes string argument as column name from which values are
        suppossed to be extracted
     """
     return tuple(set(self.get(col_name)))

   def ensure_one(self):
      """This is a method for ensuring that only one record is returned and not
         a tuple or custom_tuple of records
      """
      if len(self)==1:
        return self[0]
      else:
        raise Exception("There is more than one records")

class custom_tuple_write(custom_tuple_read):
   """This is a class for converting a normal tuple into a custom tuple
      which has some import methods like update, delete etc, for record
      manipulations
   """
   def update(self,**data):
      """This is a method helper for updating a group of specific records
         in a database with arguments as column names and their corresponding
         values for the record
      """
      for record in self:
         record.update(**data)

   def delete(self):
      """This is a method helper for deleting a group of specific records in a
         database
      """
      for record in self:
         record.delete()
