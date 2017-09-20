from flask import Flask
from flaskext.mysql import MySQL
import random, collections

## Database configuration information ####################################
app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = None
app.config['MYSQL_DATABASE_PASSWORD'] = None
app.config['MYSQL_DATABASE_DB'] = None
app.config['MYSQL_DATABASE_HOST'] = None
mysql.init_app(app)
##########################################################################

def funct_maker(name):
  """This is a method used to return objects of class tables, it allow user to
     access database table through it's name
  """

  def new_funct():
    return table(name)
  return new_funct

def configure(**data):
      """This is a method for configuring a database to be used,
         It generally accept three specified arguments which are
         db_user, db_password, db_name and db_host, it's called as
         db.configure( db_user='your_value',db_name='your_value',db_host='your_value',db_password='your_value' )
      """

      app.config['MYSQL_DATABASE_USER'] = data['db_user']
      app.config['MYSQL_DATABASE_PASSWORD'] = data['db_password']
      app.config['MYSQL_DATABASE_DB'] = data['db_name']
      app.config['MYSQL_DATABASE_HOST'] = data['db_host']

      data=mysql.connect().cursor()
      data.execute("show tables")
      all_tables=data.fetchall()
      data.close()
      for table_name in all_tables:
         globals().update({ table_name[0] : funct_maker(table_name[0]) })


class field(object):
   """This is a class used to define database fields and their constrains
   """

   def __init__(self,**data):
      self.model=""
      self.ref_field=""

      self.field={"key":None,'command': "field__name "+data['type'] }
      if len(data)==2 and 'constrain' in data:
         self.field['command']+=" "+data['constrain']
      elif len(data)==2 and 'key' in data:
         self.field['key']=data['key']
      elif len(data)==3 and 'constrain' in data and 'key' in data:
         self.field['command']+=" "+data['constrain']
         self.field['key']=data['key']
      elif len(data)==3 and 'key' in data and 'ref' in data:
         self.field['key']=data['key']
         reference=data['ref'].split('.')
         self.model=reference[0]
         self.ref_field=reference[1]
      elif len(data)==4 and 'key' in data and 'ref' in data and 'constrain' in data:
         self.field['command']+=" "+data['constrain']
         self.field['key']=data['key']
         reference=data['ref'].split('.')
         self.model=reference[0]
         self.ref_field=reference[1]
      else:
         pass


class model(object):
   """This is a class which is used to define raw database, it's inherited by all
      classes used for creating database
   """

   def create(self):
     """This is a method used to create table in a database
     """

     create_statement="create table "+str(self.__class__.__name__)+"("
     command=""
     primary=""
     foreign=""
     for fld in dir(self):
       field_val=getattr(self,fld)
       if isinstance(field_val, field):
          command=command+field_val.field['command'].replace('field__name',fld)+" ,"
          if field_val.field['key']=='primary':
             primary+=fld+" ,"
          if field_val.field['key']=='foreign':
             foreign+=', FOREIGN KEY ('+fld+') REFERENCES ' +field_val.model+ ' ('+ field_val.ref_field +')'
     primary='PRIMARY KEY('+primary[:len(primary)-1]+")"
     create_statement=create_statement+command+primary+foreign+")"
     conn=mysql.connect()
     cursor=conn.cursor()
     cursor.execute(create_statement)
     conn.commit()
     conn.close()
     cursor.close()


class table(object):
   """This is a class for defining a database table as object
   """

   def __init__(self,table_name):
     """This is a constructor method which takes table name as
        the argument and create an object from it
     """

     self.table__name__=table_name
     data=mysql.connect().cursor()
     data.execute("show columns from "+str(self.table__name__))
     all_cols=data.fetchall()
     self.table__columns__=collections.OrderedDict()
     for col_name in all_cols:
        self.table__columns__.update({str(col_name[0]): str(col_name[1])})

     data.execute("show index from "+str(self.table__name__)+" where Key_name='PRIMARY'")
     keys=data.fetchall()
     data.close()
     self.primary__keys__=collections.OrderedDict()
     for key in keys:
        self.primary__keys__.update({str(key[4]): str(self.table__columns__[key[4]])})

   @staticmethod
   def random_table():
      """This is not necessary, it's just a method which select a table name
         randomly from a list of tables in a database used and return it as
         string
      """

      command="show tables"
      data=mysql.connect().cursor()
      data.execute(command)
      all_tables=data.fetchall()
      data.close()
      rd=random.randint(0,len(all_tables)-1)
      return all_tables[rd][0]

   def sql(self,statement):
      """This is not necessary it's just a test method for executing sql statements
         as they are without any abstraction
      """

      data=mysql.connect().cursor()
      data.execute(statement)
      rec=data.fetchall()
      data.close()
      if isinstance(rec, tuple) and not len(rec)==0:
         records=self.get_objects(rec)
         return custom_tuple(records)
      else:
         return "Query done!."


   def get_objects(self,rec):
      """This is the actual method which convert records extracted form a
         database into objects, it generally create those objects from class
         record and assign them attributes corresponding to columns and their
         values as extracted from the database, It returns a normal tuple
         containing record objects
      """

      ls=[]
      for r in rec:
         ob=record()
         ob.table__name__=self.table__name__
         ob.table__columns__=self.table__columns__
         ob.primary__keys__=self.primary__keys__
         i=0
         for col in self.table__columns__:
            setattr(ob,str(col),str(r[i]))
            i=i+1;
         ls.append(ob)
      return tuple(ls)

   def get(self):
         """This is a method which returns all records from a database as
            a custom tuple of objects of record
         """

         data=mysql.connect().cursor()
         data.execute("select * from "+str(self.table__name__))
         rec=data.fetchall()
         data.close()
         return custom_tuple(self.get_objects(rec))

   def get_one(self,pri_key_with_val):
        """This is a method for getting a single specific record by using it's
           primary key(s), here the argument to this method is the dict which
           contains primary key(s) and it's/their corresponding value(s), the
           format of argument is  { primary_key1: value1, primary_key2: value2, ...}
        """

        pk=record()
        condition=pk.get_query_condition(pri_key_with_val)
        return self.where(condition)


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

         command=""
         if len(data)==3:
            col,expr,val=data[0],data[1],data[2]
            if isinstance(val,str):
              command="select * from "+str(self.table__name__)+" where "+str(col)+" "+str(expr)+" "+"'"+val+"'"
            else:
              command="select * from "+str(self.table__name__)+" where "+str(col)+" "+str(expr)+" "+str(val)

         elif len(data)==1 :
            cond=data[0]
            command="select * from "+str(self.table__name__)+" where "+cond
         else:
            raise Exception("Invalid agruments")

         data=mysql.connect().cursor()
         data.execute(command)
         data.close()
         rec=data.fetchall()
         return custom_tuple( self.get_objects(rec) )


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
      for val in data:
         if "char" in self.table__columns__[val] or "text" in self.table__columns__[val] or "date" in self.table__columns__[val] or "time" in self.table__columns__[val]:
            st=st+"'"+data[val]+"',"
         else :
            st=st+str(data[val])+","
      st=st[:len(st)-1]+")"
      return st

   def insert(self,**data):
      """This is a method which is used to insert records into a database, with
         specified arguments as colums and their corresponding values to insert
         into a database, It generally return a record which has been inserted
         into your database
      """

      command="insert into "+ str(self.table__name__) +" "+self.columns_to_insert(data)+ " values "+self.values_to_insert(data)
      conn=mysql.connect()
      cursor=conn.cursor()
      cursor.execute(command)
      conn.commit()
      conn.close()
      cursor.close()
      pri_key_with_val=collections.OrderedDict()
      for prk in self.primary__keys__:
         pri_key_with_val.update({prk:data[prk]})
      return self.get_one(pri_key_with_val)


class record(object):
   """This is a class for defining records as objects,
      It generally produce objects which corresponds to
      records extracted from a database
   """

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

   def get_query_condition(self, data):
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


   def update(self, **data):
      """This is the actual method for updating a specific record
         in a database with arguments as columns and their corresponding
         values for the record
      """

      values=self.get_query_condition(data)
      condition=self.get_query_values(self.primary__keys__)

      command="update "+ str(self.table__name__)+" set "+values+" where "+ condition.replace(',',' and')
      conn=mysql.connect()
      cursor=conn.cursor()
      cursor.execute(command)
      conn.commit()
      conn.close()
      cursor.close()


   def delete(self):
      """This is the actual method for deleting a specific record
         in a database
      """

      condition=self.get_query_values(self.primary__keys__)
      command="delete from "+ str(self.table__name__)+" where "+ condition.replace(',',' and')
      conn=mysql.connect()
      cursor=conn.cursor()
      cursor.execute(command)
      conn.commit()
      conn.close()
      cursor.close()


class custom_tuple(tuple):
   """This is a class for converting a normal tuple to a custom tuple
      with some import methods like update, delete etc, all for different
      records manipulations
   """

   def update(self,**data):
      """This is a method helper for updating specific records with inputs to
         the database as specified arguments
      """

      for rec in self:
         rec.update(**data)

   def delete(self):
      """This is a method helper for deleting specific records in a database
      """

      for rec in self:
         rec.delete()

   def count(self):
     """This is a method for counting records
     """

     return len(self)

   def ensure_one(self):
      """This is a method for ensuring that only one record is returned and not
         a tuple or custom_tuple of records
      """

      if len(self)==1:
        return self[0]
      else:
        raise Exception("There is more than one records")
