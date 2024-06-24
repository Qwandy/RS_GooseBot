# RSGooseBot
A discord bot to aid with running clan goose game events

## Plan for the project
2. Create a list of optional inputs for tiles of a goose game (limit of 100 inputs?)
    1. create command show_tiles which shows all of the tiles
    2. create command update_tile in format /update_tile (number, role_name OR role_id)
        1. using command should send a message announcing what tile the player has landed on
4. Announce what tile players have landed on
5. Look into hosting the bot
6. Make some fun commands

## What needs to be done for the event (outside of bot scope)
1. Finish planning out the tasks
2. Create a graphic of all the various tasks
3. Advertise the event and poll various things

## Documentation

### Python commands
- create_team_data(tblname): creates the table inside the tblname file (such as team_data.db)
- insert_team_data(tblname, user_id, username, role_id, rolename): inserts all of the data into a database for one user.

### Discord commands
- /text hello: greets the user
- /text flax: uses the user's name for a joke and embeds a gif in the text channel
- /create_game: reads in data from a text file to generate an embed of various tasks for the goose game.
- /update_game(role_name, integer): increases a role's (teams) points by the integer provided.
- /leaderboard: Provides an embed in the text channel with each team's position in the goose game.
