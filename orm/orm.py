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

class orm(object):
   @staticmethod
   def configure_db(**data):
      """This is a method for configuring a database to be used,
         It generally accept three specified arguments which are
         db_user, db_password, db_name and db_host, it's called as
         orm.configure_db( db_user='your_value',db_name='your_value',db_host='your_value',db_password='your_value' )
      """

      app.config['MYSQL_DATABASE_USER'] = data['db_user']
      app.config['MYSQL_DATABASE_PASSWORD'] = data['db_password']
      app.config['MYSQL_DATABASE_DB'] = data['db_name']
      app.config['MYSQL_DATABASE_HOST'] = data['db_host']


class Table(object):
   """This is a class for defining a database table as object
   """
   def __init__(self,table_name):
     """This is a constructor method which takes table name as
        the argument and create an object from it
     """

     if table_name == "":
        table_name=Table.random_table()
     self.table__name__=table_name

     command="show columns from "+str(self.table__name__)  ##Find table columns
     data=mysql.connect().cursor()
     data.execute(command)
     all_cols=data.fetchall()
     self.table__columns__=collections.OrderedDict()
     for col_name in all_cols:
        self.table__columns__.update({str(col_name[0]): str(col_name[1])})

     command="show index from "+str(self.table__name__)+" where Key_name='PRIMARY'" ##Find primary keys
     data.execute(command)
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

   def test(self):
      """This is not necessary it's just a test method
      """
      command='show create table Student';
      data=mysql.connect().cursor()
      data.execute(command)
      all_tables=data.fetchall()
      data.close()
      return all_tables


   def get_objects(self,rec):
      """This is the actual method which convert records extracted form a
         database into objects, it generally create those objects from class
         Record and assign them attributes corresponding to columns and their
         values as extracted from the database, It returns a normal tuple
         containing record objects
      """

      ls=[]
      for r in rec:
         ob=Record()
         ob.table__name__=self.table__name__
         ob.table__columns__=self.table__columns__
         ob.primary__keys__=self.primary__keys__
         i=0
         for col in self.table__columns__:
            exec("ob."+str(col)+"="+"'"+str(r[i])+"'")
            i=i+1;
         ls.append(ob)
      return tuple(ls)

   def get(self):
         """This is a method which returns all records from a database as
            a custom tuple of objects of Record
         """

         command="select * from "+str(self.table__name__);
         data=mysql.connect().cursor()
         data.execute(command)
         rec=data.fetchall()
         data.close()
         records=self.get_objects(rec)
         return custom_tuple(records)

   def get_one(self,pri_key_with_val):
        """This is a method for getting a single specific record by using it's
           primary key(s), here the argument to this method is the dict which
           contains primary key(s) and it's/their corresponding value(s), the
           format of argument is  { primary_key1: value1, primary_key2: value2, ...}
        """
        pk=Record()
        condition=pk.get_query_condition(pri_key_with_val)
        record=self.where(condition)
        return record;


   def where(self,*data):
         """This is a method which is used to query and return records from a
            database as a custom tuple of objects of Record, the criteria used
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
            return None

         data=mysql.connect().cursor()
         data.execute(command)
         data.close()
         rec=data.fetchall()
         records=self.get_objects(rec)
         return custom_tuple(records)


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

   def create(self,**data):
      """This is a method which is used to insert records into a database, with
         specified arguments as colums and their corresponding values to insert
         into a database, It generally return a record which has been inserted
         into your database
      """
      command="insert into "+ str(self.table__name__) +" "+self.columns_to_insert(data)+ " values "+self.values_to_insert(data)
      #print("\n||||||||||||||*INSERTION|||||||||||||||||||")
      #print(command)
      #print("||||||||||||||*INSERTION|||||||||||||||||||\n")
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


class Record(object):
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
      if isinstance(data,dict):
         for key in data:
           exec("val=self."+str(key))
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
      if isinstance(data,dict):
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

      condition=condition.replace(',',' and')
      command="update "+ str(self.table__name__)+" set "+values+" where "+ condition
      #print("\n||||||||||||||*UPDATE*|||||||||||||||||||")
      #print(command)
      #print("||||||||||||||*UPDATE*|||||||||||||||||||\n")
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
      condition=condition.replace(',',' and')
      command="delete from "+ str(self.table__name__)+" where "+ condition
      #print("\n|||||||||||||||*DELETION*||||||||||||||||||")
      #print(command)
      #print("|||||||||||||||*DELETION*||||||||||||||||||\n")
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

   def ensure_one(self):
      """This is a method for ensuring that only one record is returned and not
         a tuple or custom_tuple of records
      """
      if len(self)==1:
        return self[0]
      else:
        return None;
