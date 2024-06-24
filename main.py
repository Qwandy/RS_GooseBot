# imports
import discord
import dotenv
import os
from discord import channel
from typing import List, Optional, Dict
from dataclasses import dataclass
import re
import random
import math
import pandas as pd
import sqlite3


def create_task_data(txtfile):
        with open(txtfile, 'r') as f:
                lines = f.readlines()
        task_numbers = [line.split(".")[0] for line in lines]
        tasks = [line.split(".")[1].replace("\n", "") for line in lines]
        
        df = pd.DataFrame(columns=["Task Number", "Task"])
        df["Task Number"] = task_numbers
        pd.to_numeric(df["Task Number"])
        df["Task"] = tasks
        df.set_index("Task Number", drop = True, inplace=True)
        return df 

def create_team_data(tblfile):
    
    # SQL code
    sql_statements = ["""CREATE TABLE IF NOT EXISTS team_data ( \
            user_id INTEGER PRIMARY key, \
                name text NOT NULL, \
                role_id INTEGER, \
                role_name text NOT NULL, \
                board_position); """]
    
    try: 
        with sqlite3.connect(tblfile) as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)
            conn.commit()
    except sqlite3.Error as e:
        print(e)

def insert_team_data(tblname, user_id, username, role_id, rolename):
    
    # testing inserting and viewing data
    con = sqlite3.connect(tblname)
    cur = con.cursor()
    cur.execute(f"INSERT INTO team_data (user_id, name, role_id, role_name, board_position) \
    VALUES ('{user_id}', '{username}', '{role_id}', '{rolename}', '0');")

    con.commit()

def update_team_data(tblname, rolename, pts):

    # testing inserting and viewing data
    con = sqlite3.connect(tblname)
    cur = con.cursor()
    cur.execute(f"UPDATE team_data \
                SET board_position = board_position + {pts} \
                    WHERE role_name = '{rolename}'")
    con.commit()

def show_leaderboard(tblname):

    teams = []
    scores = []
    con = sqlite3.connect(tblname)
    cur = con.cursor()
    for row in cur.execute(f"SELECT role_name, board_position FROM team_data \
                            GROUP BY board_position \
                           ORDER BY board_position DESC;"):
        
        teams.append(row[0])
        scores.append(row[1])

        print(row)

    return teams, scores
# initialises the bot and connects it to discord
bot = discord.Bot()

class FunCommands():

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready and online")

    # a subgroup of commands for creating text
    text = bot.create_group("text", "Greet people")

    @text.command() # says hello to the user
    async def hello(ctx):
        await ctx.respond(f"Hello, {ctx.author}!")

    @text.command() # a meme command that says user's flax be spinning and shows a gif
    async def flax(self):
        await discord.TextChannel.send(self, content = f"**{self.author}'s flax be spinnin...**", file= discord.File("memes/osrs-flax.gif"))

class RSGooseBot():
    
    game = bot.create_group("game", "run goose game")

    @game.command()
    async def create_game(ctx):
        txtfile = 'tasks.txt'
        with open(txtfile, 'r') as f:
            lines = f.readlines()
        clean_lines = [line.replace("\n", "") for line in lines]
        print(clean_lines)

        if len(clean_lines) <= 25:
            embed = discord.Embed(
                title="Goose game tasks",
                description = "Tasks",
                color = discord.Color.blurple()
            )

            for i in range(len(clean_lines)):
                embed.add_field(name=clean_lines[i], value = "Task", inline = False)
            
            embed.set_footer(text="Footer")
            embed.set_author(name="McQwandy")

            await ctx.respond("Hello! You have successfully created an instance of a goose game!.", embed=embed)
        
        elif len(clean_lines) > 25:
            embed_nr = math.ceil(len(clean_lines) / 25)
            ctr = 0
            for i in range(embed_nr):
                embed = discord.Embed(
                title="Goose game tasks",
                description = "Tasks",
                color = discord.Color.blurple()
                )
                if ctr < 25:
                    for k in range(len(clean_lines[0:25])):
                        embed.add_field(name=clean_lines[ctr], value = "Task", inline = False)
                        ctr += 1
                        print(ctr)
                elif ctr >= 25:
                    for y in range(len(clean_lines[26:])+1):
                        embed.add_field(name=clean_lines[ctr], value = "Task", inline = False)
                        ctr += 1
                        print(ctr)
                
                    
                embed.set_footer(text="Footer")
                embed.set_author(name="McQwandy")

                await ctx.respond("Hello! You have successfully created an instance of a goose game!.", embed=embed)


    @game.command()
    async def update_game(ctx, role_name, pts):
        update_team_data('team_data.db', role_name, pts)

        for row in cur.execute("SELECT user_id, name, role_id, role_name, board_position FROM team_data"):
            print(row)
        await ctx.respond(f"Hello! You have successfully updated {role_name}'s position on the board by {pts}")

    @game.command()
    async def leaderboard(ctx):

        teams, scores = show_leaderboard("team_data.db")

        embed = discord.Embed(
                title="Goose Game Leaderboard",
                description = "Current leaderboard",
                color = discord.Color.blurple())

        for i in range(len(teams)):
            embed.add_field(name="", value = f"**{teams[i]}: {scores[i]}**", inline = False)

        embed.set_footer(text="Footer")
        embed.set_author(name="McQwandy")

        await ctx.respond(f"Hello! The current leaderboard is: ", embed = embed)
if __name__ == "__main__":
    
    dotenv.load_dotenv() # loads dotenv data into code
    token = str(os.getenv("DISCORD_TOKEN")) # gets token as private variable

    # create pandas dataframe of task data
    df_tasks = create_task_data('tasks.txt')

    create_team_data("team_data.db")

    # testing inserting and viewing data
    """con = sqlite3.connect("team_data.db")
    cur = con.cursor()
    cur.execute("INSERT INTO team_data (user_id, name, role_id, role_name, board_position) \
    VALUES ('1234', 'qwandy', '1234', 'The_Mr', '0'), \
                ('2345', 'lyra', '2345', 'The_Mrs', '0'); ")"""
    
    con = sqlite3.connect("team_data.db")
    cur = con.cursor()

    insert_team_data("team_data.db", "1234", "qwandy", "2345", "gigachad")
    insert_team_data("team_data.db", "11234", "dude mcc00l", "2345", "gigachad")
    insert_team_data("team_data.db", "2345", "lyra", "2345", "gigachadess")

    for row in cur.execute("SELECT user_id, name, role_id, role_name, board_position FROM team_data"):
        print(row)

    bot.run(token)
