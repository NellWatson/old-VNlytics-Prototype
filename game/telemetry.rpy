init python in telemetry:
    
    import urllib, urllib2, json

    host = "http://159.203.183.226:3000/v1/"
    project_id = "TestGame"
    game_id = ""

    collected_data = {}

    session = 1

    def setup():
        """
        Start the actual syncing process in a thread so the game doesn't hang.
        """

        renpy.invoke_in_thread(start_setup)

    def start_setup():
        print "Here"
        global game_id
    
        import platform

        os = platform.system()
        resolution = str((renpy.display.get_info().current_w, renpy.display.get_info().current_h))
        render = renpy.get_renderer_info()["renderer"]

        if not check_internet():
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

    def collect(data, kind):
        global collected_data

        day = str(renpy.store.day)

        if day not in collected_data:
            collected_data[day] = {}

        entry = collected_data[day]

        if kind == "choices":
            if "choices" not in entry:
                entry["choices"] = [data]
            else:
                entry["choices"].append(data)
        elif kind not in entry["data"]:
            entry["data"][kind] = [data]
        else:
            entry["data"][kind].append(data)

    def sync():
        """
        Start the actual syncing process in a thread so the game doesn't hang.
        """

        # Save the collected data and url locally since we are in a different thread now and
        # the collected_data dict can change while we are syncing.

        url = host + project_id + "/" + game_id + "/"
        renpy.invoke_in_thread(start_sync, available_data=collected_data, url=url)

    def start_sync(available_data, url):

        if not check_internet():
            return "No Internet Connection"

        for entry, stats in available_data.items():
            data = {
                "day": entry
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
                return "No Internet Connection"

            print response.read()
            del collected_data[entry]

    def check_internet():

        try:
            response=urllib2.urlopen(host, timeout=10)
            return True
        except urllib2.URLError:
            return False

    def new_session():
        global session

        session += 1

    def end():

        # Save the url locally since we are in a different thread now

        url = host + project_id + "/" + game_id + "/end/"
        renpy.invoke_in_thread(actual_end, url=url)

    def actual_end(url):
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

init python:

    class CollectTelemetry(Action):

        def __init__(self, data, kind):
            self.data = data
            self.kind = kind

        def __call__(self):
            telemetry.collect(self.data, self.kind)

    if not hasattr(persistent, "multiple_id"):
        persistent.multiple_id = False

    def label_callback(name, via):
        store.present = name

    config.label_callback = label_callback
