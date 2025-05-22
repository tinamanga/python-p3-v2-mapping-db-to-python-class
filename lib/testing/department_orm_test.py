import pytest
from department import Department
from __init__ import CURSOR, CONN


class TestDepartment:
    '''Class Department in department.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''Drop tables prior to each test.'''

        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        Department.all = {}

    def test_creates_table(self):
        '''Contains method "create_table()" that creates table "departments" if it does not exist.'''

        Department.create_table()
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'").fetchone()
        assert result is not None

    def test_drops_table(self):
        '''Contains method "drop_table()" that drops table "departments" if it exists.'''

        Department.create_table()
        Department.drop_table()
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments'").fetchone()
        assert result is None

    def test_saves_department(self):
        '''Contains method "save()" that saves a Department instance to the db and assigns the instance an id.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        sql = """
            SELECT * FROM departments
        """
        row = CURSOR.execute(sql).fetchone()
        assert (row[0], row[1], row[2]) == (department.id, "Payroll", "Building A, 5th Floor")

    def test_creates_department(self):
        '''Contains method "create()" that creates a new row in the db using parameter data and returns a Department instance.'''

        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        sql = """
            SELECT * FROM departments
        """
        row = CURSOR.execute(sql).fetchone()
        assert (row[0], row[1], row[2]) == (department.id, "Payroll", "Building A, 5th Floor")

    def test_updates_row(self):
        '''Contains a method "update()" that updates an instance's corresponding db row to match its new attribute values.'''
        Department.create_table()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        id1 = department1.id
        department2 = Department.create("Marketing", "Building B, 3rd Floor")
        id2 = department2.id

        # Assign new values for name and location
        department2.name = "Sales and Marketing"
        department2.location = "Building B, 4th Floor"

        # Persist the updated name and location values
        department2.update()

        # assert department1 row was not updated
        department = Department.find_by_id(id1)
        assert department.id == id1
        assert department.name == "Human Resources"
        assert department.location == "Building C, East Wing"

        # assert department2 row was updated
        department = Department.find_by_id(id2)
        assert department.id == id2
        assert department.name == "Sales and Marketing"
        assert department.location == "Building B, 4th Floor"

    def test_deletes_row(self):
        '''Contains a method "delete()" that deletes the instance's corresponding db row'''
        Department.create_table()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        id1 = department1.id
        department2 = Department.create("Sales and Marketing", "Building B, 4th Floor")
        id2 = department2.id

        department2.delete()

        # assert department1 row was not deleted, department1 object state is correct
        department = Department.find_by_id(id1)
        assert (department.id, department.name, department.location) == (id1, "Human Resources", "Building C, East Wing")

        # assert department2 row is deleted
        department = Department.find_by_id(id2)
        assert department is None

    def test_instance_from_db(self):
        '''Contains method "instance_from_db()" that takes a table row and returns a Department instance.'''

        Department.create_table()
        Department.create("Payroll", "Building A, 5th Floor")

        sql = """
            SELECT * FROM departments
        """
        row = CURSOR.execute(sql).fetchone()
        department = Department.instance_from_db(row)

        assert (row[0], row[1], row[2]) == (department.id, "Payroll", "Building A, 5th Floor")

    def test_gets_all(self):
        '''Contains method "get_all()" that returns a list of Department instances for every row in the db.'''

        Department.create_table()

        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        departments = Department.get_all()

        assert len(departments) == 2
        assert (departments[0].id, departments[0].name, departments[0].location) == (department1.id, "Human Resources", "Building C, East Wing")
        assert (departments[1].id, departments[1].name, departments[1].location) == (department2.id, "Marketing", "Building B, 3rd Floor")

    def test_finds_by_id(self):
        '''Contains method "find_by_id()" that returns a Department instance corresponding to the db row retrieved by id.'''

        Department.create_table()
        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        department = Department.find_by_id(department1.id)
        assert (department.id, department.name, department.location) == (department1.id, "Human Resources", "Building C, East Wing")

        department = Department.find_by_id(department2.id)
        assert (department.id, department.name, department.location) == (department2.id, "Marketing", "Building B, 3rd Floor")

        department = Department.find_by_id(0)
        assert department is None

    def test_finds_by_name(self):
        '''Contains method "find_by_name()" that returns a Department instance corresponding to the db row retrieved by name.'''

        Department.create_table()
        department1 = Department.create("Human Resources", "Building C, East Wing")
        department2 = Department.create("Marketing", "Building B, 3rd Floor")

        department = Department.find_by_name("Human Resources")
        assert (department.id, department.name, department.location) == (department1.id, "Human Resources", "Building C, East Wing")

        department = Department.find_by_name("Marketing")
        assert (department.id, department.name, department.location) == (department2.id, "Marketing", "Building B, 3rd Floor")

        department = Department.find_by_name("Unknown")
        assert department is None