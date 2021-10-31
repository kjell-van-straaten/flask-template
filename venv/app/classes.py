class User:
  def __init__(self, id, username, password, role, team):
    self.id = id
    self.username = username
    self.password = password
    self.role = role
    self.team = team

  def __repr__(self):
    return f'<User: {self.username}>'