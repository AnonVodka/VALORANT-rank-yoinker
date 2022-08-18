from colr import color

class Colors:
    def __init__(self, agent_dict, AGENTCOLORLIST):
        self.agent_dict = agent_dict
        self.AGENTCOLORLIST = AGENTCOLORLIST

    def get_color_from_team(self, team, name, playerPuuid, selfPuuid):
        if team == 'Red':
            Teamcolor = color(name, fore=(238, 77, 77))
        elif team == 'Blue':
            Teamcolor = color(name, fore=(76, 151, 237))
        else:
            Teamcolor = ''
        if playerPuuid == selfPuuid:
            Teamcolor = color(name, fore=(221, 224, 41))
        return Teamcolor

    def level_to_color(self, level):
        if level >= 400:
            return color(level, fore=(0, 255, 255))
        elif level >= 300:
            return color(level, fore=(255, 255, 0))
        elif level >= 200:
            return color(level, fore=(0, 0, 255))
        elif level >= 100:
            return color(level, fore=(241, 144, 54))
        elif level < 100:
            return color(level, fore=(211, 211, 211))

    def get_agent_from_uuid(self, agentUUID):
        agent = str(self.agent_dict.get(agentUUID))
        if self.AGENTCOLORLIST.get(agent.lower()) != None:
            agent_color = self.AGENTCOLORLIST.get(agent.lower())
            return color(agent, fore=agent_color)
        else:
            return agent
