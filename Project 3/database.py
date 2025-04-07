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
    
    def remove_user(self, addr):
        if addr.name in self.users:
            del self.users[addr.name]

    def create_group(self, name, key, admin_name):
        if name in self.groups:
            return False  # Grupo já existe
        self.groups[name] = Group(name, key, admin_name.name)
        admin_name.join_group(name)
        return True
    
    def get_user_by_address(self, addr):    
        for user in self.users.values():
            if user.address == addr:
                return user
        return None

    def delete_group(self, group_name, user):
        group=self.groups.get(group_name)
        if user.name == group.admin:
            del self.groups[group_name]
            for user_name in self.users.values():
                if group_name in user.groups:
                    user.leave_group(group_name)
            return True
        else:
            return False

    def get_online_users(self):
        return list(self.users.keys())

    def get_groups(self, user):
        return user.list_groups()

    def get_mygroups(self, user):
        my_groups=[]
        
        for group_name, group_obj in self.groups.items():
            if group_obj.admin == user.name:
                my_groups.append(group_name)
                
        return my_groups
    
    def add_user_to_group(self, group_name, group_key, user_name):
        group = self.groups.get(group_name)
        if not group:
            return False
        elif group.key != group_key:
            return False
        else:
            user_name.join_group(group_name)
            return group.add_member(user_name)
        
    def remove_user_from_group(self, group_name, user_name):
        group = self.groups.get(group_name)
        if not group:
            return False
        else:
            return group.remove_member(user_name)
    def ban_from_group(self,ban_username, admin_user):
        for group_name in ban_username.groups:
            if group_name in admin_user.groups:
                group = self.groups.get(group_name)
                if group and group.admin == admin_user.name:
                    return group.ban_user(ban_username)
        return False
    def get_friends(self, addr):
        return addr.list_friends()
    
    def add_friend(self, friend_name, addr):
        username = self.get_user_by_address(addr)
        return self.users[username.name].follow(friend_name)
    
    def remove_friend(self, friend_name, addr):
        username = self.get_user_by_address(addr)
        return self.users[username.name].unfollow(friend_name)