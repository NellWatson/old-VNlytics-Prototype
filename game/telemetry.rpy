init python in telemetry:
    
    import urllib, urllib2, json

    host = "http://159.203.183.226:3000/v1/"
    project_id = "TestGame"
    game_id = ""

    collected_data = {}
    last_synced_block = {}

    session = 1
    status = ""

    def setup():
        """
        Start the actual syncing process in a thread so the game doesn't hang.
        """

        renpy.invoke_in_thread(_setup)

    def _setup():
        """
        Queries the server to generate a game id that will be used for saving game data.
        """

        global game_id, status
    
        import platform

        status = "setup"
        os = platform.system()
        resolution = str((renpy.display.get_info().current_w, renpy.display.get_info().current_h))
        render = renpy.get_renderer_info()["renderer"]

        if not check_internet():
            game_id = "placeholder"
            return "No Internet connection."

        payload = {
            "project_id": project_id,
            "platform": os,
            "display_render": render,
            "display_size": resolution,
            "multiple_ids": renpy.store.persistent.multiple_id
        }

        data = json.dumps(payload)

        r = urllib2.Request(host + project_id, data, { "Content-Type": "application/json" })
        response = urllib2.urlopen(r)

        game_id = response.read()[1:-1]
        renpy.store.persistent.multiple_id = True
        renpy.store.persistent.seen_choice_labels[game_id] = set()
        renpy.store.persistent.game_pass[game_id] = 0

        status = ""

    def collect(data, kind):
        global collected_data, game_pass, status, sync_now

        while status == "setup":
            continue

        status = "collecting"
        day = str(renpy.store.day)

        # If for some reason no game_id has been generated, generate one.
        if game_id == "placeholder":
            setup()

            if game_id != "placeholder":
                collected_data[game_id] = collected_data["placeholder"]
                del collected_data["placeholder"]

        if day not in collected_data:
            collected_data[day] = {}

        entry = collected_data[day]

        if kind == "choices":
            if "choices" not in entry:
                entry["choices"] = [data]
            else:
                entry["choices"].append(data)

            # If the player has previously seen this choice, update the game_pass variable.
            if data["label"] in renpy.store.persistent.seen_choice_labels[game_id]:
                renpy.store.persistent.game_pass[game_id] += 1
            else:
                renpy.store.persistent.seen_choice_labels[game_id].update({ data["label"] })

        elif kind not in entry["data"]:
            entry["data"][kind] = [data]
        else:
            entry["data"][kind].append(data)

        status = ""

    def sync():
        """
        Start the actual syncing process in a thread so the game doesn't hang.
        """

        # Save the collected data and url locally since we are in a different thread now and
        # the collected_data dict can change while we are syncing.

        while status:
            continue

        if game_id == "placeholder":
            setup()
            return

        url = host + project_id + "/" + game_id + "/"
        renpy.invoke_in_thread(_sync, available_data=collected_data, url=url)

    def _sync(available_data, url):

        global status, last_synced_block

        status = "syncing"

        if not check_internet():
            return "No Internet Connection"

        # This is to prevent values from being resubmitting in case when the player
        # uses a combination of skipping and super fast clicking
        for i in last_synced_block.keys():
            if i in available_data:
                if available_data[i]["choices"] == last_synced_block[i]["choices"]:
                    del available_data[i]

        # Store the current data
        last_synced_block = available_data.copy()

        for entry, stats in available_data.items():
            data = {
                "day": entry,
                "game_pass": renpy.store.persistent.game_pass[game_id]
                }

            if "choices" in stats:
                data["choices"] = stats["choices"]

            if "data" in stats:
                data["data"] = stats["data"]

            data = json.dumps(data)

            try:
                r = urllib2.Request(url, data, { "Content-Type": "application/json" })
                response = urllib2.urlopen(r)
            except Exception, e:
                print str(e)
                last_synced_block = {}
                return "No Internet Connection"

            print response.read()

            # When two choices are placed back to back and player fast clicks + skips through them,
            # the entry will be removed but it's reference will remain in one of the threads.
            try:
                del collected_data[entry]
            except KeyError:
                pass

        status = ""

    def check_internet():
        """
        Returns True if Internet connection is present, otherwise, returns False
        """

        try:
            urllib2.urlopen(host, timeout=10)
            return True
        except urllib2.URLError:
            return False

    def new_session():
        global session

        session += 1

    def end():

        # Save the url locally since we are in a different thread now

        if game_id == "placeholder":
            setup()
            return

        url = host + project_id + "/" + game_id + "/end/"
        renpy.invoke_in_thread(_end, url=url)

    def _end(url):
        data = {
            "ending": "None",
            "play_time": 100
            }

        data = json.dumps(data)

        try:
            r = urllib2.Request(url, data, { "Content-Type": "application/json" })
            response = urllib2.urlopen(r)
        except Exception, e:
            print str(e)
            return "No Internet Connection"

        print response.read()

    def compare_data():

        if not check_internet():
            return "No Internet Connection"

        renpy.invoke_in_thread(_compare_data, project_id=project_id, game_id=game_id)

    def _compare_data(project_id, game_id):
        game_url = host + project_id + "/" + game_id + "/get"
        project_url = host + project_id + "/choices"
        
        _data = {}
        _chosen_captions = []

        response = urllib2.urlopen(game_url)
        game_data = json.load(response)

        response = urllib2.urlopen(project_url)
        project_data = json.load(response)

        # Find out which choices the player made
        for i in game_data:
            for j in i["choices"]:
                _chosen_captions.append(( j["label"], j["caption"] ))

        for i in project_data:
            _temp = {}
            _total = 0

            for j in i["choices"]:
                value = False
                _total += j["count"]

                if (i["label"], j["caption"]) in _chosen_captions:
                    value = True
                
                _temp[ j["caption"] ] = [ j["count"], value]

            _temp["total"] = _total
            _data[ i["label"] ] = _temp

        renpy.store.compare_data_store = _data

init python:

    class CollectTelemetry(Action):

        def __init__(self, data, kind):
            self.data = data
            self.kind = kind

        def __call__(self):
            telemetry.collect(self.data, self.kind)

    if not persistent.multiple_id:
        persistent.multiple_id = False

    if not persistent.seen_choice_labels:
        persistent.seen_choice_labels = {}

    if not persistent.game_pass:
        persistent.game_pass = {}

    def label_callback(name, via):
        store.present = name

    config.label_callback = label_callback
