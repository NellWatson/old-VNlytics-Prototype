# You can place the script of your game in this file.

# Declare images below this line, using the image statement.
# eg. image eileen happy = "eileen_happy.png"

# Declare characters used by this game.

init python:
    import store.telemetry as telemetry

define e = Character('Eileen', color="#c8ffc8")
default day = 2
default game_id = "fn_" + "".join([renpy.random.choice('0123456789abcdefghij') for x in range(8)])

# The game starts here.
label start:
    $ telemetry.setup()

    $ persistent.multiple_id = True
    $ print telemetry.game_id

    # telemetry.new_day()

    e "You've created a new Ren'Py game."
    e "Once you add a story, pictures, and music, you can release it to the world!"
    e "Here comes your first Choice."

    menu first_choice:
        "First":
            "You choose first"
        "Second":
            "You choose second"

    $ telemetry.sync()

    $ day = 3

    menu second_choice:
        "Third":
            "You choose first"
        "Fourth":
            "You choose second"

    menu third_choice:
        "Fifth":
            "You choose first"
        "Sixth":
            "You choose second"

    $ telemetry.sync()
    $ telemetry.end()

    return
