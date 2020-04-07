from sqlalchemy.exc import IntegrityError

from app import db
import pandas as pd
from app.models import Player, Club, League, Transfer

df = pd.read_json('data/transfers-20200131.json', lines=True)

for i in range(len(df)):
    try:
        club_from = df["from"][i]["leagueId"]
        club_to = df["to"][i]["leagueId"]
        value = df["transfer"][i]["value"]
        position = df["player"][i]["position"]
        if club_from == "" or club_to == "" or value == "" or value == "?" or value == "draft" or \
                value == "Available for free transfer" or value == "-" or value == "Free transfer" or value == '0' or \
                position == "":
            continue
        else:
            """if position == 'Centre-Forward' or position == 'Second Striker' or position == 'Forward' or position == 'Left Winger' or position == 'Right Winger':
                position = 'Forward'
            elif position == 'Right-Back' or position == 'Defender' or position == 'Left-Back' or position == 'Centre-Back':
                position = 'Defender'
            elif position == 'Central Midfield' or position == 'Attacking Midfield' or position == 'Midfielder' or position == 'Right Midfield' or position == 'Left Midfield' or position == 'Defensive Midfield':
                position = 'Midfielder'
            else:
                position = df["player"][i]["position"]

            player = Player(id=df["player"][i]["href"], name=df["player"][i]["name"],
                            position=position, age=df["player"][i]["age"],
                            img_href=df["player"][i]["image"], nationality=df["player"][i]["nationality"])
            db.session.add(player)"""
            
            """league1 = League(id=df["from"][i]["leagueId"], href=df["from"][i]["leagueHref"],
                             name=df["from"][i]["league"], country=df["from"][i]["country"])
            db.session.add(league1)"""

            """league2 = League(id=df["to"][i]["leagueId"], href=df["to"][i]["leagueHref"],
                             name=df["to"][i]["league"], country=df["from"][i]["country"])
            db.session.add(league2)"""

            """from_var = Club(id=df["from"][i]["href"], name=df["from"][i]["name"], country=df["from"][i]["country"],
                            country_img_href=df["from"][i]["countryImage"], leagueId=df["from"][i]["leagueId"],
                            club_img_href=df["from"][i]["image"])
            db.session.add(from_var)"""

            """to_var = Club(id=df["to"][i]["href"], name=df["to"][i]["name"], country=df["to"][i]["country"],
                          country_img_href=df["to"][i]["countryImage"], leagueId=df["to"][i]["leagueId"],
                          club_img_href=df["to"][i]["image"])
            
            db.session.add(to_var)"""

            transfer = Transfer(playerId=df["player"][i]["href"], id=df["transfer"][i]["href"],
                                value=df["transfer"][i]["value"], timestamp=df["transfer"][i]["timestamp"],
                                fromId=df["from"][i]["href"], toId=df["to"][i]["href"], season=df["season"][i],
                                fromLeagueId=df["from"][i]["leagueId"], toLeagueId=df["to"][i]["leagueId"],
                                fromCountry=df["from"][i]["country"], toCountry=df["to"][i]["country"])
            db.session.add(transfer)
            db.session.commit()

    except IntegrityError as e:
        print(e)
        db.session.rollback()




