from users_groups import User,Group
class Database:
    def __init__(self):
        self.users = {}  # Nome -> User
        self.groups = {} # Nome do grupo -> Group

    def add_user(self, name, address):
        if name in self.users:
            return False  # Usuário já existe
        self.users[name] = User(name, address)
        return True

    def remove_user(self, name):
        if name in self.users:
            del self.users[name]

    def create_group(self, name, key, admin_name):
        if name in self.groups:
            return False  # Grupo já existe
        self.groups[name] = Group(name, key, admin_name)
        return True
    
    def get_user_by_address(self, addr):    
        for user in self.users.values():
            if user.address == addr:
                return user
        return None


    def delete_group(self, name):
        if name in self.groups:
            del self.groups[name]

    def get_online_users(self):
        return list(self.users.keys())

    def get_groups(self):
        return list(self.groups.keys())