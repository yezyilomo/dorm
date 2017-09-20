# x_orm
  This is a tool that lets you query and manipulate data from sql database using an object-oriented paradigm in flask framework
  
# How to use it?
  $ git clone https://github.com/yezyilomo/x_orm.git
  
  $ cd x_orm
  
  $ pip install 
  
  Then you can start using it in your flask application 
  
  For those who want to contribute codes are available at x_orm/orm/orm.py 
  
  # Resources
  [Flask framework official documentation](http://flask.pocoo.org/)
  
  
  
  
# DORM API DOCUMENTATION

This is a simple user documentation, illustrating how to use dorm tool, dorm API provides the following methods for data manipulations

1.configure(**data):

      This is a static method for configuring a database to be used,

      It generally accept three specified arguments which are

      db_user, db_password, db_name and db_host, it's called as

      db.configure( db_user='your_value',db_name='your_value',db_host='your_value',db_password='your_value' )

      and it has to be called at the beginning of config.py file


2.get():

      This is a method which returns all records from a database as

      a tuple of objects of records, it takes no arguments and it's called as

      db.table_name().get()


3.where(*data):

      This is a method which is used to query and return records from a

      database as a tuple of objects of records, the criteria used

      to query records is specified as argument(s), This method accept two

      forms of arguments, the first form is three specified arguments which

      form a query condition

      eg  db.table_name().where('age', '>', 20)

      and the second form is a single argument which specify a query condition

      for instance in the first example we could obtain the same result by using

      db.table_name().where('age > 20')    


4.insert(**data):

      This is a method which is used to insert records into a database, with

      specified arguments as columns and their corresponding values to insert

      into a database, It generally return a record which has been inserted

      into your database, it can be called as

      db.table_name().insert(Reg_No='2018-04-003', Name='Yezy Ilomo', Age=22)


5.update(**data):

      This is a method for updating records in a database with arguments

      as columns and their corresponding values for the record, it's called as

      db.table_name().where('age', '>', 20).update(Category="Adult")

      this will update Category field for all records in Student table where age

      is greater than 20 with "Adult" value,

      You can also update all records regardless of any condition in your table as

      db.table_name().get().update(Category="Adult")


6.delete():      

      This is a method for deleting records in a database, it takes no arguments

      it can be used to delete all records in your table as

      db.table_name().get().delete()

      and if you want to delete records basing on a specific condition you can

      also use it with where() clause as

      db.table_name().where('age', '>', 20).delete()  or as

      db.table_name().where('age > 20').delete()


7.ensure_one():

      This is a method which returns a single record object which you can access

      its attributes(record values ) by using dot operator on this function with

      the name of column that you want to access its value, The method will return

      None if it's applied to a tuple which contains more than one record, and it's

      called as

      db.table_name().where('Reg_No = "2015-05-033"').ensure_one()

      on this object you can access record fields as

      db.table_name().where('Reg_No = "2015-05-033"').ensure_one().Reg_No or

      db.table_name().where('Reg_No = "2015-05-033"').ensure_one().name   or

      db.table_name().where('Reg_No = "2015-05-033"').ensure_one().Course  etc.

8.sql(query):

      This is a method which allows you to execute normal SQL statements without

      abstraction, this is used in case you want to do operation that is not supported

      by the API. This method accept one string argument which is the sql statement

      to be executed, and it's called as

      db.table_name().sql('your sql statement')

      for example db.table_name().sql('select * from Student where age>18')

      Note sql should involve table used in db.table_name()


# Table attributes

      A table has several attributes which might help in data manipulation which are

      1. table__columns__ this store all table columns and their corresponding data types

         as a dictionary in form of { column_name: data_type }

         You can access table__columns__ attribute as

         db.table_name().table__columns__


      2. table__name__  this store table name as a string

         You can access it as

         db.table_name().table__columns__


      3. primary__keys__ this store table primary keys and their corresponding data types

         as a dictionary inform of  { primary_key_name: data_type }

         You can access primary__keys__  attribute as

         db.table_name().primary__keys__

# Record attributes
      Record has all attributes that table has(mentioned above), in addition to that
      Record has data attributes corresponding to each record field name(column name)
      these data attributes are used to access record fields from record object      

