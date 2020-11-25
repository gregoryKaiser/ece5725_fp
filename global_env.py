#class for global objects/effects

class environment(object):
    def __init__(self, global_x, effect_length, env_type, attack):
        self.global_x = global_x
        self.effect_length = effect_length
        self.type = env_type
        self.attack = attack
    
    def do_harm(self, hero):
        #not sure whether to do location check here or in main??
        if hero.env_type != self.env_type:
            hero.health -= self.attack
