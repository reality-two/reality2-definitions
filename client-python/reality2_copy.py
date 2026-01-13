import json
import asyncio
import ssl
import aiohttp
import websockets

class Reality2:
    def __init__(self, domain_name, port, ssl=True):
        self.__secure = ssl
        protocol = "https" if ssl else "http"
        ws_protocol = "wss" if ssl else "ws"
        self.__graphql_http_url = f"{protocol}://{domain_name}:{port}/reality2"
        self.__graphql_webs_url = f"{ws_protocol}://{domain_name}:{port}/reality2/websocket"
        self.__events = []

    async def close(self):
        for event in self.__events:
            event.set()

    async def __graphql_post(self, query, variables):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.__graphql_http_url, json={"query": query, "variables": variables}, ssl=False) as response:
                    result = await response.json()
                    return result.get("data", {})
            except Exception:
                return {}

    async def sentantAll(self, passthrough={}, details="id name"):
        return {**passthrough, **await self.__graphql_post(self.__sentant_all(details), {})}

    async def sentantGet(self, id="", passthrough={}, details="id name"):
        return {**passthrough, **await self.__graphql_post(self.__sentant_get_by_id(details), {"id": id})}

    async def sentantGetByName(self, name="", passthrough={}, details="id name"):
        return {**passthrough, **await self.__graphql_post(self.__sentant_get_by_name(details), {"name": name})}

    async def sentantUnload (self, id, passthrough = {}, details = "id name"):
        return {**passthrough, **self.__graphql_post(self.__sentant_unload(details), {"id": id})}
    
    async def sentantUnloadByName (self, name, passthrough = {}, details = "id name"):
        response = self.sentantGetByName(name, {}, details="id")
        if ("sentantGet" in response):
            try:
                return {**passthrough, **self.__graphql_post(self.__sentant_unload(details), {"id": response["sentantGet"]["id"]})}
            except:
                return {}
        else:
            return {}
    
    async def sentantUnloadAll (self, passthrough = {}):
        try:
            sentants = self.sentantAll()
            for sentant in sentants["sentantAll"]:
                return self.sentantUnload(sentant["id"], passthrough)
        except:
            return None

    async def awaitSignal(self, id, signal, callback=None, details="event parameters passthrough sentant { id name description }"):
        event = asyncio.Event()
        self.__events.append(event)
        asyncio.create_task(self.__subscribe(self.__graphql_webs_url, id, signal, callback, details, event))

    async def __subscribe(self, server, sentantid, signal, callback, details, running):
        join_message = {"topic": "__absinthe__:control", "event": "phx_join", "payload": {}, "ref": 0}
        subscribe = {"topic": "__absinthe__:control", "event": "doc", "payload": {"query": self.__await_signal(details), "variables": {"id": sentantid, "signal": signal}}, "ref": 0}

        ssl_context = None
        if self.__secure:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        async with websockets.connect(server, ssl=ssl_context) as websocket:
            await websocket.send(json.dumps(join_message))
            response = await websocket.recv()
            if not self.__check_status(response):
                return

            await websocket.send(json.dumps(subscribe))
            response = await websocket.recv()
            if not self.__check_status(response):
                return

            asyncio.create_task(self.__heartbeat(websocket, running))

            while not running.is_set():
                message = await websocket.recv()
                message_json = json.loads(message)
                payload = message_json.get("payload", {})
                if "result" in payload and callback:
                    callback(payload["result"]["data"])

    async def __heartbeat(self, websocket, running):
        heartbeat = {"topic": "phoenix", "event": "heartbeat", "payload": {}, "ref": 0}
        while not running.is_set():
            await asyncio.sleep(30)
            await websocket.send(json.dumps(heartbeat))

    def __check_status(self, message):
        message_dict = json.loads(message)
        return message_dict.get("payload", {}).get("status") == "ok"

    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Await Signal definition
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __await_signal (self, details):
        return (
        """
        subscription AwaitSignal($id: UUID4!, $signal: String!) {
            awaitSignal(id: $id, signal: $signal) {
                """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Load Swarm definition
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __swarm_load (self, details):
        return (
        """
        mutation SwarmLoad($definition: String!) {
            swarmLoad(definition: $definition) {
                description
                name
                sentants {
                    """ + details + """
                }
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Send Event definition
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __sentant_send (self, details):
        return (
        """
        mutation SentantSend($id: String!, $event: String!, $parameters: Json, $passthrough: Json) {
            sentantSend(id: $id, event: $event, parameters: $parameters, passthrough: $passthrough) {
            """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Load a Sentant definition
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __sentant_load (self, details):
        return (
        """
        mutation SentantLoad($definition: String!) {
            sentantLoad(definition: $definition) {
                """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Unload a Sentant
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __sentant_unload (self, details):
        return (
        """
        mutation SentantUnload($id: UUID4!) {
            sentantUnload(id: $id) {
                """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Get a Sentant's details
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __sentant_get_by_id (self, details):
        return (
        """
        query SentantGet($id: UUID4) {
            sentantGet(id: $id) {
                """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Get a Sentant's details
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __sentant_get_by_name (self, details):
        return (
        """
        query SentantGet($name: String) {
            sentantGet(name: $name) {
                """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Get all Sentant's details
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __sentant_all (self, details):
        return (
        """
        query SentantAll {
            sentantAll {
                """ + details + """
            }
        }
        """
    )
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Static methods
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def JSONPath(data, path):
        paths = path.split(".")
        currentData = data
        for index, subpath in enumerate(paths):
            if subpath == "[]" and isinstance(currentData, list):
                newCurrentData = []
                remaining_path = "" if index == len(paths)-1 else ".".join(paths[index+1:])
                for item in currentData:
                    newCurrentData.append(Reality2.JSONPath(item, remaining_path))
                return newCurrentData
            elif isinstance(currentData, list) and subpath.isdigit():
                currentData = currentData[int(subpath)]
            elif isinstance(currentData, dict):
                if subpath in currentData:
                    currentData = currentData[subpath]
                else:
                    return None
            else:
                return None
        return currentData
    # --------------------------------------------------------------------------------------------------------------------------------------------------

