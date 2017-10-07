# Decent Object-Relational Mapper(DORM)
  This is a tool that lets you query, insert, update, create, delete and manipulate data from SQL database using object-oriented paradigm in flask web framework

# How to use it?
  $ pip3 install dorm

  Then you can start using it in your flask application,

  Note: dorm depend on (flask, ilo, flask-mysql, sha3), thus installing it

  will install all these dependencies automatically if you don't have them in

  your system.

  For those who want to contribute codes are available at dorm/dorm/db.py

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


2.get(col_name): In context of records

      This is a method which returns all records from a database as

      a tuple of objects of records if it takes no arguments, but if it's

      given a string argument it return a tuple of values in a specified column

      name(argument), and it's called as

      db.table_name().get()   or

      db.table_name().get(col_name)   or

      db.table_name().where('condition').get('col_name')  


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

      into a database, it also accept values if record insertions involve all

      columns It generally return a record which has been inserted

      into your database, it can be called as

      db.table_name().insert(Reg_No='2018-04-003', Name='Yezy Ilomo', Age=22)  or

      db.table_name().insert(2018-04-003', Yezy Ilomo',22)


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

8.execute(sql_statement):

      This is a method which allows you to execute normal SQL statements without

      abstraction, this is used in case you want to do operation that is not supported

      by the API. This method accept single arguments which is, the sql statement

      to be executed, and it's called as

      db.execute('your sql statement')

      for example db.execute('select * from Student where age>18')

9.create():

      This is a method which is used in creating database tables, it's an instance

      method of class which defines a table, all classes which defines tables are

      placed in 'database/raw_db.py' file, for example a class defining a table Student

      might look like

      class Student(db.model):

          reg_No=db.field(type="char(10)",constrain="not null",key="primary")

          full_name=db.field(type="char(30)",constrain="not null")

          age=db.field(type="int")

          course=db.field(type="char(20)", constrain="not null")

          year_of_study=db.field(type="int", constrain="not null")


      a corresponding table from above class can be created by instantiating

      an object of Student class and calling a method 'create' in 'run' method as

      def run():

         Student().create()

10.join(table,join_type):

      This is a method which is used in joining database tables with first

      arguments as table to join to, and second argument as join type which

      is inner by default, this method return an object of joined table and

      it's called as

      db.table1_name().join(table2,'your_join_type')

11.on(*on_condition):

      This is a method which does the actual joining and return records according

      to the conditions specified in join condition, it accept two form of arguments,

      the first form is a three arguments which form the join condition eg

      db.table1().join(table2).on('table1.id','=','table2.id')

      and the second form is a single string which Specify the whole condition eg

      db.table1().join(table2).on('table1.id = table2.id')

12.hash(string):

      This is a method which is used to hash information(eg passwords) for

      privacy purpose, it uses sha3 to hash and add some characters to the

      hashed string for increasing security, it takes a string arguments to

      be hashed and it returns hashed string

13.select(*columns, **kwargs ):

      This is a method which is used to select several columns to be included

      in SQL query, it accept a number of arguments which are column names passed

      as strings, if you want to select all columns except few columns you can pass

      all_except=['column1', 'column2', ...] as kwarg, It's called as

      db.table_name().select('column1', 'column2', ...)   

      if you want to use all_except property, you call it as

      db.table_name().select(all_except=['column1', 'column2', ...])

14.getdistinct(column_name):

      This is a method for extracting distinct values in a specified column,

      it takes string argument as column name from which distinct values are

      suppossed to be extracted

15.find(primary_key1='value', primary_key2='value',.....):

      This is a method for finding a single specific record by using it's

      primary key(s), here the argument to this method is the dict which

      contains primary key(s) and it's/their corresponding value(s), this

      method is called as

      db.table_name.find( primary_key1='value', primary_key2='value', primary_key3='value', ..... )

16.max(column_name):

      This is a method for evaluating maximum value in a given column passed as

      an argument to it, it's called as

      db.table_name.max( column_name ).get() or with where clause as

      db.table_name.max( column_name ).where( condition )

      you can also do other calculations eg

      db.table_name.max( '2021-birth_year' ).where( condition )

17.min(column_name):

      This is a method for evaluating minimum value in a given column passed as

      an argument to it, it's called as

      db.table_name.min( column_name ).get() or with where clause as

      db.table_name.min( column_name ).where( condition )

      you can also do other calculations eg

      db.table_name.min( '2021-birth_year' ).where( condition )

18.avg(column_name):

      This is a method for evaluating average value in a given column passed as

      an argument to it, it's called as

      db.table_name.avg( column_name ).get() or with where clause as

      db.table_name.avg( column_name ).where( condition )

      you can also do other calculations eg

      db.table_name.avg( '2021-birth_year' ).where( condition )        

19.count(column_name):

      This is a method for counting number of records in a table/result

      it's called as

      db.table_name.count().get() or with where clause as

      db.table_name.count().where( condition )

20.get(): In context of calculation

      This is a method which returns a value when applied to a table of type calculation

      Note: only max(),  min(), avg() and count() return a table of type calculation,

      Therefore when this method is applied on them it returns a value depending on

      what it's calculated, eg to calculate the average age of all student in table

      student you may do it as

      db.student().avg('age').get()  this will return average value

# Table and Joined Table attributes

      A table has several attributes which might help in data manipulation which are

      1. table__columns__ this store all table columns as a list,

         You can access table__columns__ attribute as

         db.table_name().table__columns__


      2. table__name__  this store table name as a string

         You can access it as

         db.table_name().table__columns__

      3. table__type__ this store a table type ie actual or partial or calculation

         You can access it as

         db.table_name().table__type__   

      4. primary__keys__ this store table primary keys as a list

         You can access primary__keys__  attribute as

         db.table_name().primary__keys__

      5. selected__columns__ this store columns used in select statement,

         and it's '*'/all columns by default unless it's changed by user

# Record attributes

      Record has all attributes that table has(mentioned above), in addition to that

      Record has data attributes corresponding to each record field name(column name)

      these data attributes are used to access record fields from record object      
