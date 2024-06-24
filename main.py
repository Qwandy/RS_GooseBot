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
        # reads in text file data by line
        with open(txtfile, 'r') as f:
                lines = f.readlines()
        task_numbers = [line.split(".")[0] for line in lines] # number for each task in the goose game
        tasks = [line.split(".")[1].replace("\n", "") for line in lines] # tasks for the goose game
        
        df = pd.DataFrame(columns=["Task Number", "Task"]) # pandas dataframe
        df["Task Number"] = task_numbers # inserts task numbers into column
        pd.to_numeric(df["Task Number"]) # converts task numbers from string to numeric
        df["Task"] = tasks # inserts tasks into task column
        df.set_index("Task Number", drop = True, inplace=True) # sets index to task number column
        return df 

def create_team_data(tblfile):
    
    # Creates schema for SQL table
    sql_statements = ["""CREATE TABLE IF NOT EXISTS team_data ( \
            user_id INTEGER PRIMARY key, \
                name text NOT NULL, \
                role_id INTEGER, \
                role_name text NOT NULL, \
                board_position); """]
    
    try: 
        with sqlite3.connect(tblfile) as conn: # connects to table with sqlite3
            cursor = conn.cursor() # creates a cursor object
            for statement in sql_statements:
                cursor.execute(statement) # executes SQL query
            conn.commit() # saves changes to .db file
    except sqlite3.Error as e: 
        print(e) # exception: prints error

def insert_team_data(tblname, user_id, username, role_id, rolename):
    
    # testing inserting and viewing data
    con = sqlite3.connect(tblname)
    cur = con.cursor()

    # inserts function parameters into SQL table
    cur.execute(f"INSERT INTO team_data (user_id, name, role_id, role_name, board_position) \
    VALUES ('{user_id}', '{username}', '{role_id}', '{rolename}', '0');")

    con.commit() # commit changes to .db file

def update_team_data(tblname, rolename, pts):

    # testing inserting and viewing data
    con = sqlite3.connect(tblname)
    cur = con.cursor()

    # update a team's points
    cur.execute(f"UPDATE team_data \
                SET board_position = board_position + {pts} \
                    WHERE role_name = '{rolename}'")
    con.commit() # commit changes to .db file

def show_leaderboard(tblname):

    # empty lists to append to
    teams = []
    scores = []

    con = sqlite3.connect(tblname) # connect to table
    cur = con.cursor() # create cursor object
    
    # creates small table with role name and board position for displaying information in discord
    for row in cur.execute(f"SELECT role_name, board_position FROM team_data \
                            GROUP BY board_position \
                           ORDER BY board_position DESC;"):
        
        # appends data to empty list
        teams.append(row[0])
        scores.append(row[1])

        print(row) # for debugging / visualisation

    return teams, scores # returns data

# initialises the bot and connects it to discord
bot = discord.Bot()

class FunCommands():

    # message for when bot joins server
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
    
    # creates a subgrouo of commands with prefix /game
    game = bot.create_group("game", "run goose game")

    @game.command()
    async def create_game(ctx): # creates an embed displaying tasks read in from a txt file
        '''
        Reads in data from a text file and uses it to embed data in a Discord text channel.
        '''

        txtfile = 'tasks.txt'
        with open(txtfile, 'r') as f:
            lines = f.readlines() # reads in data by line
        clean_lines = [line.replace("\n", "") for line in lines] #cleans up data by removing newline code
        print(clean_lines) # print for debugging / visualisation

        if len(clean_lines) <= 25: # max limit for a discord embed is 25 fields
            embed = discord.Embed(
                title="Goose game tasks",
                description = "Tasks",
                color = discord.Color.blurple()
            )
            
            # adds tasks to the embed
            for i in range(len(clean_lines)):
                embed.add_field(name=clean_lines[i], value = "Task", inline = False)
            
            # some pycord embed stuff they like you to use 
            embed.set_footer(text="Footer")
            embed.set_author(name="McQwandy")

            # await command for asynchronous function, includes embed.
            await ctx.respond("Hello! You have successfully created an instance of a goose game!.", embed=embed)
        
        # conditional for splitting up embed into multiple if more than 25 tasks.
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
        '''
        Updates the state of the game for a team
        '''


        update_team_data('team_data.db', role_name, pts)
        
        current_pts = None # empty variable to alter for display
        con = sqlite3.connect('team_data.db') # create connection to table
        cur = con.cursor() # create cursor object
        for row in cur.execute(f"SELECT DISTINCT board_position FROM team_data \
                    WHERE role_name = '{role_name}'"): # query to get a specific team's points
            current_pts = row # changes empty variable to current points

        #for row in cur.execute("SELECT user_id, name, role_id, role_name, board_position FROM team_data"):
            #print(row)

        # await for asynchronous function
        await ctx.respond(f"Hello! You have successfully updated {role_name}'s position on the board by {pts}. Your current position is {current_pts[0]}.")

    @game.command()
    async def leaderboard(ctx):
        '''
        Displays the leaderboard
        '''
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

    # Creates the table schema
    create_team_data("team_data.db")
    
    con = sqlite3.connect("team_data.db")
    cur = con.cursor()

    # Inserts some users into the game, will be replaced with a <read from text file, loop function> method
    insert_team_data("team_data.db", "1234", "qwandy", "2345", "gigachad")
    insert_team_data("team_data.db", "11234", "dude mcc00l", "2345", "gigachad")
    insert_team_data("team_data.db", "2345", "lyra", "2345", "gigachadess")

    # display / visualisation
    for row in cur.execute("SELECT user_id, name, role_id, role_name, board_position FROM team_data"):
        print(row)

    # runs the bot
    bot.run(token)
