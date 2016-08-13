# You can place the script of your game in this file.

# Declare images below this line, using the image statement.
# eg. image eileen happy = "eileen_happy.png"

# Declare characters used by this game.

init python:
    import store.telemetry as telemetry

define e = Character('Eileen', color="#c8ffc8")

default day = 2
default compare_data_store = None
default show_order = [ "first_choice", "second_choice", "third_choice" ]

# The game starts here.
label start:
    $ telemetry.setup()

    $ persistent.multiple_id = True
    $ print telemetry.game_id

    e "You've created a new Ren'Py game."
    e "Once you add a story, pictures, and music, you can release it to the world!"
    e "Here comes your first Choice."

    menu first_choice:
        "First":
            "You choose first."
        "Second":
            "You choose second."

    $ telemetry.sync()

    $ day = 3

    menu second_choice:
        "Third":
            "You choose third."
        "Fourth":
            "You choose fourth."

    menu third_choice:
        "Fifth":
            "You choose fifth."
        "Sixth":
            "You choose sixth."

    $ telemetry.sync()

    "Thank you for playing the game."

    $ telemetry.end()
    $ telemetry.compare_data()

    call screen check

    return

screen check():

    add Solid("#00000050")

    if not compare_data_store:
        text "Please while we fetch the data" size 60 xalign 0.5 yalign 0.5
    else:
        vbox:
            spacing 10
            xalign 0.5
            yalign 0.5
                
            for i in show_order:
                $ c = compare_data_store[i]

                button:
                    text i size 30 bold True underline True
                    background "#00000000"

                vbox:
                    spacing 15
                    xpos 80

                    for j in c:
                        if j != "total":
                            $ _percent = round(c[j][0] * 100.00 / c["total"], 2)

                            if c[j][1]:
                                text "* " + j + " -- " + str(_percent) + "%" underline True
                            else:
                                text j + " -- " + str(_percent) + "%"

    textbutton _("return"):
        action Return()

        align (1.0, 1.0)
