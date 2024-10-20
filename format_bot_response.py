import os
import random

class GlorpResponses():

    def GetBannedListMessage(self, open_ban_slots, banned_glorps):
        message = f"# :prohibited: Banishment\n\nType `=Ban \"Glorp Name\"` to add a Glorp to your banishment list. Glorps on your ban list will be removed from the wheel before you spin it."
        message += f"\n\nType `=Ban Remove \"Glorp_Name\"` to remove a Glorp from your ban list. Ban slots are awared by Glorps that carry the banishment perk."
        message += f"\n\nYou have `{open_ban_slots}` banishment slots available.\n"
        used_slots = 1
        for i, glorp in enumerate(banned_glorps):
            used_slots += 1
            message += f"\n`Banishment Slot {i + 1}: {glorp[0]}`"
        for i in range(open_ban_slots):
            message += f"\n`Banishment Slot {i + used_slots}: Empty`"
        return message
    
    def GetSacricicePointsDescription(self, sac_points):
        if sac_points == 1:
            return "A faint sensation courses through your body. Was it ever really there?"
        elif sac_points == 2:
            return "What is this feeling? The seeds of power?"
        elif sac_points == 3:
            return "Your fingers contort as you absorb a dark energy."
        elif sac_points == 4:
            return "You body thrums with the power of an unnatural force."
        elif sac_points == 5:
            return "Your eyes crackle as a dark energy envelops you. What is happening?"
        elif sac_points == 6:
            return "A rapidly filling well of unlimited power. You feel it coursing through your veins. "
        elif sac_points == 7:
            return "You can hardly contain the souls of your victims. What will be unleashed?"
        else:
            return "Nothing happened. Was the sacrificed denied?"
    
    def GetSacrificePointsFromGlorpCard(self, stars):
        if stars == 1:
            points = 2 if random.uniform(0, 1) < 0.33 else 1
        if stars == 2:
            points = 3
        if stars == 3:
            points = 5
        if stars == 4:
            points = 8 if random.uniform(0, 1) < 0.4 else 7
        if stars >= 5:
            points = 10
        return points
 
    def GetImagePath(self, file_name):
        script_directory = os.path.dirname(__file__)
        relative_path = f"Images/{file_name}"
        return os.path.join(script_directory, relative_path)

    def PadWithString(variable, string, count):
        for i in range(count):
            variable += string
        return variable

    def GetSpinOutcomeText(self, display_name, stars, spawn_type = "spin", quantity = 1):
        star_descriptions = {1:'A common variant.', 2:'An uncommon Glorp.', 3:'An unlikely find.', 4:'A rare species!', 5:'An amazing catch!', 6:'A stupendous specimen!'}
        star_decorator_text = star_descriptions.get(stars, "An unknown variant?")

        star_emojis = GlorpResponses.PadWithString("", "★", stars)
        star_emojis = GlorpResponses.PadWithString(star_emojis, "✰", 6 - stars)


        punctuation = "find!" if stars > 3 else "find."

        if spawn_type == "craft":
            sugar_text = "You have successfully crafted the"
        elif spawn_type == "sacrifice":
            if quantity > 1 and display_name == "Eye":
                sugar_text = f"You have summoned **{quantity}** of the"
            else:
                sugar_text = "You have summoned the"
        else:
            sugar_text = "The wheel has granted you the"
        

        return f"{sugar_text} `{display_name}`. {star_decorator_text}\n{star_emojis}\n"
    
    def GetDetailedViewDescription(self, glorp_data):
        traits = []
        message = ""
        if glorp_data[7] == 1:
            traits.append("crafting")
        if glorp_data[8] == 1:
            traits.append("sacrificing")
        if glorp_data[9] == 1:
            traits.append("gambling")

        if len(traits) > 0:
            message = f"This Glorp can be used for"
        if len(traits) == 1:
            message += f" {traits[0]}."
        if len(traits) == 2:
            message += f" {traits[0]} and {traits[1]}."
        if len(traits) == 3:
            message += f" {traits[0]}, {traits[1]}, and {traits[2]}."

        if glorp_data[12] == 1:
            message += "\n\n" if message else ""
            message += f"-# *{glorp_data[2]} **thrums** with an unknown power...*" 

        return message
