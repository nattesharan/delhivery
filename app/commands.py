from flask_script import Command
from app.settings import ROLES
from delhivery.models import DelhiveryHierarchy
class CreateRoles(Command):

    def run(self):
        print("Creating roles in database")
        for role in ROLES:
            DelhiveryHierarchy.objects.create(name=role['name'], role=role['role'], features=role['features'])

def add_command(manager):
    manager.add_command('initroles', CreateRoles())