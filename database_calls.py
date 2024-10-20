import sqlite3
import random
import datetime

'''
INT [ 0] glorp_id
STR [ 1] file_name
STR [ 2] display_name
INT [ 3] stars
INT [ 4] has_hat
INT [ 5] spinnable
INT [ 6] craftable
INT [ 7] is_ingredient     
INT [ 8] can_sacrifice
INT [ 9] can_gamble
INT [10] spin_odds
INT [11] gamble_odds
INT [12] perk
DAT [13] created
DAT [14] last_updated
'''

class GlorpDB():

    # spin_cooldown = 1800
    # TODO Change spin cooldown before deployment.
    spin_cooldown = 1800
    database_name = "glorp.db"
    enraged_glorp = 38
    prison_glorp = 35
    glorp_limit = 50
    enraged_glorp_rewards = [57, 37, 24] # Livid = 57, Enraged = 37, Mad = 24

    def Write(query, parameters = {}, execute_many = False):
        connection = sqlite3.connect(GlorpDB.database_name)
        cursor = connection.cursor()

        if execute_many:
            cursor.executemany(query, parameters)
        else:
            cursor.execute(query, parameters)

        connection.commit()

        cursor.close()
        connection.close()
        return

    def Fetch(query, parameters = {}, fetch_one = False):
        connection = sqlite3.connect(GlorpDB.database_name)
        cursor = connection.cursor()

        if parameters:
            cursor.execute(query, parameters)
        else:
            cursor.execute(query)

        if fetch_one:
            result = cursor.fetchone()
        else:
            result = cursor.fetchall()

        cursor.close()
        connection.close()
        return result
    
    def GetUserGlorpCollection(self, user_id, sort_alpha = False):
        glorp_count = GlorpDB.GetUsersGlorpCount(user_id)
        pluralize = "Glorp" if glorp_count == 1 else "Glorps"
        glorp_list = GlorpDB.QueryDatabaseForUserGlorps(user_id, sort_alpha=sort_alpha)
        message = f"# :mag: Your Glorpedex\nType `=View \"Glorp_Name\"` for more detailed information.\n\nType `=View Sort` for an alphabetized view of your Glorps.\n\n-# You have **{glorp_count}** {pluralize} in your collection.\n"
        for item in glorp_list:
            star_emojis = GlorpDB.PadWithString("", "✰", 6 - item[2])
            star_emojis = GlorpDB.PadWithString(star_emojis, "★", item[2])
            message += f"\n`{star_emojis} {item[1]} ({item[3]}`)"
        return message
    
    def PadWithString(variable, string, count):
        for i in range(count):
            variable += string
        return variable

    def AddGlorpToUserBanList(self, user_id, glorp_id):
        query = "INSERT INTO user_bans (user_id, glorp_id) VALUES (:user_id, :glorp_id)"
        parameters = {"user_id" : user_id, "glorp_id" : glorp_id}
        GlorpDB.Write(query=query, parameters=parameters)
        return
    
    def RemoveGlorpFromUserBanList(self, user_id, glorp_id):
        query =  "DELETE FROM user_bans WHERE user_id = :user_id AND glorp_id = :glorp_id"
        parameters = {"user_id" : user_id, "glorp_id" : glorp_id}
        GlorpDB.Write(query=query, parameters=parameters)
        return
    
    def QueryDatabaseForUserBanSlotCount(self, user_id):
        liminal_glorp_id = 56
        query = "SELECT COUNT(*) FROM user_glorps WHERE user_id = :user_id AND glorp_id = :glorp_id"
        parameters = {"user_id" : user_id, "glorp_id" : liminal_glorp_id}
        result = GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
        return 0 if not result[0] else 2
    
    def GetGlorpsInUsersBannedList(self, user_id):
        query =  """SELECT g.display_name
                    FROM glorp_cards AS g
                    JOIN user_bans AS u
                    ON g.glorp_id = u.glorp_id
                    WHERE user_id = :user_id"""
        parameters = {"user_id" : user_id}
        return GlorpDB.Fetch(query=query, parameters=parameters)
        
    def QueryDatabaseForUserGlorps(user_id, sort_alpha = False):
        if sort_alpha:
            query =  """SELECT file_name, display_name, stars, COUNT(u.glorp_id)
                        FROM (SELECT glorp_id, user_id FROM user_glorps WHERE user_id=:user_id) AS u
                        JOIN glorp_cards AS g
                        ON u.glorp_id = g.glorp_id
                        GROUP BY display_name
                        ORDER BY display_name ASC"""
        else:
            query =  """SELECT file_name, display_name, stars, COUNT(u.glorp_id)
                        FROM (SELECT glorp_id, user_id FROM user_glorps WHERE user_id=:user_id) AS u
                        JOIN glorp_cards AS g
                        ON u.glorp_id = g.glorp_id
                        GROUP BY display_name
                        ORDER BY stars DESC, display_name ASC"""
        parameters = {"user_id" : user_id}
        return GlorpDB.Fetch(query=query, parameters=parameters)

    def GetUsersGlorpCount(user_id):
        query = "SELECT COUNT(user_id) FROM user_glorps WHERE user_id = :user_id"
        parameters = {"user_id" : user_id}
        count = GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
        return count[0]
    
    def UserIsBelowGlorpLimit(self, user_id):
        glorp_count = GlorpDB.GetUsersGlorpCount(user_id)
        return True if glorp_count < GlorpDB.glorp_limit else False

    def GetAllSpinnableGlorpIds():
        query = "SELECT glorp_id, spin_odds FROM glorp_cards WHERE spin_odds > :spin_odds"
        parameters = {"spin_odds" : 0}
        return GlorpDB.Fetch(query=query, parameters=parameters)
    
    def GetAllGambleGlorps():
        query = "SELECT glorp_id, gamble_odds FROM glorp_cards WHERE gamble_odds > :gamble_odds"
        parameters = {"gamble_odds" : 0}
        return GlorpDB.Fetch(query=query, parameters=parameters)
        
    def GetBestGlorpFromGlorpGambleData(spins):
        gamble_odds = random.uniform(0 , 100)
        for i in range(spins):
            next_spin = random.uniform(0, 100)
            gamble_odds = gamble_odds if gamble_odds < next_spin else next_spin
        query = "SELECT glorp_id FROM glorp_cards WHERE gamble_odds >= :gamble_odds ORDER BY gamble_odds ASC"
        parameters = {"gamble_odds" : gamble_odds}
        glorp_data = GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
        return 0 if not glorp_data else glorp_data[0]
    
    def ReturnGambleOddsOfGlorp(glorp_id, glorp_data):
        for glorp in glorp_data:
            if glorp_id == glorp[0]:
                return glorp[1]
        return 100

    def GetUsersBannedGlorpIds(user_id):
        query = "SELECT glorp_id FROM user_bans WHERE user_id = :user_id"
        parameters = {"user_id" : user_id}
        return GlorpDB.Fetch(query=query, parameters=parameters)

    def RemoveValuesFromList(list, filter):
        return [value for value in list if value != filter]

    def GetRandomSpinnableGlorp(user_id):
        glorp_spin_data = GlorpDB.GetAllSpinnableGlorpIds()
        choices = []
        for item, weight in glorp_spin_data:
            choices.extend([item] * weight)
        banished_glorps = GlorpDB.GetUsersBannedGlorpIds(user_id)
        if banished_glorps:
            for row in banished_glorps:
                choices = GlorpDB.RemoveValuesFromList(choices, row[0])
        return random.choice(choices)
    
    def ParseGlorpDataForGambling(glorp_data, user_luck = 0):
        return {"glorp_id" : glorp_data[0], "spins" : glorp_data[1] * 3, "id" : glorp_data[2]}
    
    def GetUsersSacrificePoints(self, user_id):
        query = "SELECT sac_points FROM users WHERE user_id = :user_id"
        parameters = {"user_id" : user_id}
        result =  GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
        return 0 if not result else result[0]
    
    def UserHasPrisonCardInCollection(self, user_id):
        query = "SELECT COUNT(*) FROM user_glorps WHERE user_id = :user_id AND glorp_id = :glorp_id"
        parameters = {"user_id" : user_id, "glorp_id" : GlorpDB.prison_glorp}
        result = GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
        return result[0]
        
    def GlorpInUsersCollection(user_id, glorp_name):
        query =  """SELECT u.glorp_id, g.stars, u.id, g.can_gamble, g.can_sacrifice
                    FROM user_glorps AS u
                    JOIN glorp_cards AS g
                    ON u.glorp_id = g.glorp_id
                    WHERE LOWER(g.display_name) = LOWER(:glorp_name) AND u.user_id = :user_id"""
        parameters = {"glorp_name" : glorp_name, "user_id" : user_id}
        return GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
    
    def GetCraftableGlorp(self, glorp_name):
        if glorp_name.lower() == "eclipse":
            glorp_name = random.choice(["Solar Eclipse", "Lunar Eclipse"])
        query =  """SELECT g.glorp_id, c.requirements, c.rewards, g.display_name
                    FROM glorp_cards AS g
                    JOIN crafting AS c
                    ON g.glorp_id = c.glorp_id
                    WHERE g.craftable = 1 AND LOWER(g.display_name) = LOWER(:glorp_name)"""
        parameters = {"glorp_name" : glorp_name}
        result = GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
        return result if not result else {"glorp_id" : result[0], "ingredients" : result[1].split(), "rewards" : result[2].split(), "glorp_name" : result[3]}
    
    def UserIsMissingIngredients(self, user_id, ingredients):
        query = "SELECT glorp_id FROM user_glorps WHERE user_id = :user_id AND ("
        where_clauses = []
        parameters = {"user_id" : user_id}
        for i, item in enumerate(ingredients):
            where_clauses.append(f"glorp_id = :glorp_id_{i}")
            parameters[f"glorp_id_{i}"] = item
        query = f"{query}{" OR ".join(where_clauses)})"
        result = GlorpDB.Fetch(query=query, parameters=parameters)
        for set in result:
            for item in set:
                for ingredient in ingredients.copy():
                    if int(item) == int(ingredient):
                        ingredients.remove(ingredient)
        return ingredients

    def GetBannableGlorpInfo(self, display_name):
        query = "SELECT display_name, spinnable, glorp_id FROM glorp_cards WHERE LOWER(display_name) = LOWER(:display_name) LIMIT 1"
        parameters = {"display_name" : display_name}
        return GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)

    def GetGlorpDataFromGlorpID(glorp_id):
        query = "SELECT * FROM glorp_cards WHERE glorp_id = :glorp_id"
        parameters = {"glorp_id" : glorp_id}
        return GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)

    def GetMultipleGlorpDataFromGlorpId(glorp_id_list):
        where_clause = []
        parameters = {}
        for i, glorp_id in enumerate(glorp_id_list):
            parameters[f"glorp_id_{i}"] = glorp_id
            where_clause.append(f"glorp_id = :glorp_id_{i}")

        query = f"SELECT * FROM glorp_cards WHERE {" OR ".join(where_clause)}"
        return GlorpDB.Fetch(query=query, parameters=parameters)

    def GetGlorpDataFromUserIdAndName(self, user_id, glorp_name):
        query =  """SELECT g.*
                    FROM user_glorps AS u
                    JOIN glorp_cards AS g
                    ON u.glorp_id = g.glorp_id
                    WHERE LOWER(g.display_name) = LOWER(:glorp_name) AND u.user_id = :user_id"""
        parameters = {"user_id" : user_id, "glorp_name" : glorp_name}
        return GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)

    def GetLastSpinFromUserID(user_id):
        query = "SELECT last_spin FROM users WHERE user_id = :user_id"
        parameters = {"user_id" : user_id}
        return GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)
    
    def AddMultipleGlorpsToUserCollection(user_id, glorp_id_list):
        query = "INSERT INTO user_glorps (user_id, glorp_id) VALUES (?, ?)"
        parameters = []
        for glorp_id in glorp_id_list:
            parameters.append((user_id, glorp_id))
        GlorpDB.Write(query=query, parameters=parameters, execute_many=True)
        return

    def AddGlorpToUserCollection(user_id, glorp_id):
        query = "INSERT INTO user_glorps (user_id, glorp_id) VALUES (:user_id, :glorp_id)"
        parameters = {"user_id" : user_id, "glorp_id" : glorp_id}
        GlorpDB.Write(query=query, parameters=parameters)
        return

    def UpdateUserLastSpinTime(user_id):
        query = "UPDATE users SET last_spin = (datetime('now', 'localtime')) WHERE user_id = :user_id"
        parameters = {"user_id" : user_id}
        GlorpDB.Write(query=query, parameters=parameters)
        return

    def UpdateUserSacrificePoints(self, user_id, sac_points):
        query = "UPDATE users SET sac_points = :sac_points WHERE user_id = :user_id"
        parameters = {"sac_points" : sac_points, "user_id" : user_id}
        GlorpDB.Write(query=query, parameters=parameters)
        
    def CraftGlorp(self, user_id, glorp_id, ingredients):
        GlorpDB.AddGlorpToUserCollection(user_id, glorp_id)
        return GlorpDB.GetGlorpDataFromGlorpID(glorp_id)

    def DeleteMultipleGlorpsFromUsersCollection(self, user_id, ingredients):
        query = f"DELETE FROM user_glorps WHERE id = (SELECT id FROM user_glorps WHERE user_id = ? AND glorp_id = ? LIMIT 1);"
        parameters = []
        for item in ingredients:
            parameters.append((user_id, item))
        GlorpDB.Write(query=query, parameters=parameters, execute_many=True)
        return
    
    def GetIdForGlorpInUsersCollection(self, user_id, glorp_name):
        query =  """SELECT id FROM user_glorps AS u
                    JOIN glorp_cards AS g
                    ON u.glorp_id = g.glorp_id
                    WHERE user_id = :user_id
                    AND LOWER(g.display_name) = LOWER(:glorp_name)
                    LIMIT 1"""
        parameters = {"user_id" : user_id, "glorp_name" : glorp_name}
        return GlorpDB.Fetch(query=query, parameters=parameters, fetch_one=True)

    def SpinForGlorp(self, user_id):

        glorp_id = GlorpDB.GetRandomSpinnableGlorp(user_id)
        glorp_id_list = [glorp_id]

        if glorp_id == GlorpDB.enraged_glorp:
            glorp_id_list = GlorpDB.enraged_glorp_rewards
            GlorpDB.AddMultipleGlorpsToUserCollection(user_id=user_id, glorp_id_list=glorp_id_list)
        else:
            GlorpDB.AddGlorpToUserCollection(user_id, glorp_id)

        GlorpDB.UpdateUserLastSpinTime(user_id)
        return GlorpDB.GetMultipleGlorpDataFromGlorpId(glorp_id_list)
            
    def GetSacrificeRewards(self, user_id):
        glorp_id_list = [51]
        result = {}
        if random.uniform(0, 1) <= 0.25: # 25% chance to give additional Eye.
            glorp_id_list.append(51)
            result["eye_count"] = 2
        else:
            result["eye_count"] = 1

        if random.uniform(0, 1) <= 0.25: # 25% chance to give Prime II instead of Prime.
            glorp_id_list.append(66)
        else:
            glorp_id_list.append(65)

        GlorpDB.AddMultipleGlorpsToUserCollection(user_id=user_id, glorp_id_list=glorp_id_list)
        result["glorp_data"] = GlorpDB.GetMultipleGlorpDataFromGlorpId(glorp_id_list)
        return result
    
    def GambleGlorp(user_id, gambled_glorp_data):
        glorp_id = GlorpDB.GetBestGlorpFromGlorpGambleData(gambled_glorp_data["spins"])
        if not glorp_id:
            glorp_data = ("Bust")
        else:
            GlorpDB.AddGlorpToUserCollection(user_id, glorp_id)
            glorp_data = GlorpDB.GetGlorpDataFromGlorpID(glorp_id)
        GlorpDB.DeleteGlorpFromUsersCollection(gambled_glorp_data["id"])
        return glorp_data
    
    def DeleteSacrificedGlorpFromUsersCollection(self, user_id, id):
        GlorpDB.DeleteGlorpFromUsersCollection(id)
        return
    
    def DiscardGlorp(self, id):
        GlorpDB.DeleteGlorpFromUsersCollection(id)
        return

    def DeleteGlorpFromUsersCollection(id):
        query =  "DELETE FROM user_glorps WHERE id = :id"
        parameters = {"id" : id}
        GlorpDB.Write(query=query, parameters=parameters)
        return
        
    def ConvertStringToDateTime(timestamp_string):
        format_string = "%Y-%m-%d %H:%M:%S"
        datetime_obect = datetime.datetime.strptime(timestamp_string, format_string)
        return datetime_obect
    
    def CreateNewUser(user_id, user_name):
            query = "INSERT INTO users (user_id, user_name) VALUES (:user_id, :user_name)"
            parameters = {"user_id":user_id, "user_name":user_name}
            GlorpDB.Write(query=query, parameters=parameters)
            return

    def GetSecondsElapsedSinceLastUserSpin(user_id, user_name):
        last_spin_string = GlorpDB.GetLastSpinFromUserID(user_id)
        if last_spin_string is None:
            GlorpDB.CreateNewUser(user_id, user_name)
            return GlorpDB.spin_cooldown
        else:
            last_spin = GlorpDB.ConvertStringToDateTime(last_spin_string[0])
            difference = datetime.datetime.now() - last_spin
            return difference.seconds

    def UserCanSpin(self, last_spin_delta):
        return last_spin_delta >= GlorpDB.spin_cooldown
    
    def FormatTimeUntilNextSpinFromSeconds(seconds_since_last_spin):
        total_seconds = GlorpDB.spin_cooldown - seconds_since_last_spin
        if total_seconds < 60:
            return f"{total_seconds} seconds"
        else:
            return f"{total_seconds // 60} minutes and {total_seconds % 60} seconds"