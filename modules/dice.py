from .variables import VariableCommands
from utils import safe_int
from random import randint

DICE_LIST = ['2', '3', '4']

class DiceCommands(VariableCommands):
    def __init__(self, client, *args, **kwargs):
        super(DiceCommands, self).__init__(client, *args, **kwargs)
        self.commands.update({
            "roll":
                {"args": ["user", "str", "str"], "func": self.roll_dice}
        })
        
        for dice_size in DICE_LIST:
            self.commands.update({
                "d" + dice_size:
                    {"args": ["user", "str"], "func": self._roll_dice_generator(dice_size)}
            })
        
    def _roll_dice_generator(self, dice_size):
        async def _roll_specific(user, num_dice='1'):
            return await self.roll_dice(user, dice_size, num_dice)
        return _roll_specific
        
    def _parse_dice_size(self, user, dice_size):
        if dice_size is None:
            dice_size = self.db[(user.id, "dice", "size")]
        if dice_size.lower().startswith('d'):
            dice_size = dice_size[1:]
            
        dice_size = safe_int(dice_size)
        if dice_size < 2:
            dice_size = 2
            
        return dice_size

    async def roll_dice(self, user, dice_size=None, num_dice='1'):
        if num_dice.lower().startswith('d'):
            old_dice_size = dice_size
            dice_size = self._parse_dice_size(user, num_dice)
            num_dice = safe_int(old_dice_size)
        else:
            dice_size = self._parse_dice_size(user, dice_size)
            num_dice = safe_int(num_dice)
        
        out = dict()
        out["Dice size"] = (str(num_dice) + " x " if num_dice > 1 else "") + "d" + str(dice_size)
        result = 0
        for x in range(num_dice):
            result += randint(1, dice_size)
        #message = self.db[(user.id, "dice", str(dice_size), str(result))]
        out["Result"] = "You rolled a " + ("total of " if num_dice > 1 else "") + str(result) #+ (" " if message else "") + message
        return out
