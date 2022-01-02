class User:
  def __init__(self, id, username, password, role, team):
    self.id = id
    self.username = username
    self.password = password
    self.roles = self.generate_roles(role)
    self.team = team

  def __repr__(self):
    return f'<User: {self.username}>'

  def generate_roles(self, role):
    mapping = {'admin': ['toto', 'boetepotmeester', 'boetepotlezer'], 'toto': ['toto', 'boetepotlezer'], 'boetepotmeester': ['boetepotmeester', 'boetepotlezer'], 'none': ['boetepotlezer']}

    return mapping[role]
