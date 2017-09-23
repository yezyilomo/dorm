# Decent Object-Relational Mapping(DORM)
  This is a tool that lets you query and manipulate data from sql database using an object-oriented paradigm in flask framework

# How to use it?
  $ git clone https://github.com/yezyilomo/dorm.git

  $ cd dorm

  $ pip install

  Then you can start using it in your flask application

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

  8.sql(query, table):

        This is a method which allows you to execute normal SQL statements without

        abstraction, this is used in case you want to do operation that is not supported

        by the API. This method accept two arguments which are, the sql statement

        to be executed and table name involved in a query, and it's called as

        db.sql('your sql statement', 'table_name')

        for example db.sql('select * from Student where age>18', 'Student')

        Note table_name should be equal to the one in your query statement

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

  11.onwhere(on_condition, where_condition):

        This is a method which is used to query and return records from a table

        arose as a result of joining two tables, with arguments as 'ON' condition and

        'WHERE' condition, it returns a tuple of objects of record


  # Table and Joined Table attributes

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
