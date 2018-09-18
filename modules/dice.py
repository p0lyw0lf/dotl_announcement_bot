from .variables import VariableCommands
from utils import safe_int
from random import randint

class DiceCommands(VariableCommands):
    def __init__(self, client, *args, **kwargs):
        super(DiceCommands, self).__init__(client, *args, **kwargs)
        self.commands.update({
            "roll":
                {"args": ["user", "int"], "func": self.roll_dice}
        })

    async def roll_dice(self, user, dice_size=None):
        if dice_size is None:
            dice_size = safe_int(self.db[(user.id, "dice", "size")])
        if dice_size < 2:
            dice_size = 2
        out = dict()
        out["Dice size"] = str(dice_size)
        result = randint(1, dice_size)
        message = self.db[(user.id, "dice", str(dice_size), str(result))]
        out["Result"] = "You rolled a {}!".format(result) + (" " if message else "") + message
        return out
