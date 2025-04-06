class User:
    def __init__(self, name, address):
        self.name = name
        self.address = address
        self.friends = set()
        self.groups = set()

    def follow(self, friend_name):
        self.friends.add(friend_name)

    def unfollow(self, friend_name):
        self.friends.discard(friend_name)

    def join_group(self, group_name):
        self.groups.add(group_name)

    def leave_group(self, group_name):
        self.groups.discard(group_name)

    def list_groups(self):
        return list(self.groups)

    def list_friends(self):
        return list(self.friends)
    
    def __str__(self):
        return f"User({self.name}, {self.address})"
class Group:
    def __init__(self, name, key, admin):
        self.name = name
        self.key = key
        self.admin = admin
        self.members = set()
        self.banned_users = set()

    def add_member(self, user_name):
        if user_name not in self.banned_users:
            self.members.add(user_name)
            return True
        return False

    def remove_member(self, user_name):
        self.members.discard(user_name)

    def ban_user(self, user_name):
        if user_name == self.admin:
            self.members.discard(user_name)
            self.banned_users.add(user_name)
            return True
        else:
            return False
            
    def __str__(self):
        return f"Group({self.name}, Admin: {self.admin}, Members: {list(self.members)})"