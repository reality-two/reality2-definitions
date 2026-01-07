# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Reality2 class for connecting to a Reality2 Node
# Author: Roy Davies, 2024, roycdavies.github.io
# Version: 0.0.1
# ------------------------------------------------------------------------------------------------------------------------------------------------------
import json
import time
import threading
import logging
import warnings
from websockets.sync.client import connect
import ssl

import requests
import urllib3.exceptions

# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Configure logging
# ------------------------------------------------------------------------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
# ------------------------------------------------------------------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Custom Exception Classes
# ------------------------------------------------------------------------------------------------------------------------------------------------------
class Reality2Error(Exception):
    """Base exception for Reality2 client errors."""
    pass


class Reality2ConnectionError(Reality2Error):
    """Raised when connection to Reality2 node fails."""
    pass


class Reality2TimeoutError(Reality2Error):
    """Raised when a request times out."""
    pass


class Reality2ResponseError(Reality2Error):
    """Raised when the server returns an invalid or error response."""
    pass


class Reality2GraphQLError(Reality2Error):
    """Raised when GraphQL returns an error."""
    pass
# ------------------------------------------------------------------------------------------------------------------------------------------------------



# ------------------------------------------------------------------------------------------------------------------------------------------------------
# Reality2 class for connecting to a Reality2 Node
# ------------------------------------------------------------------------------------------------------------------------------------------------------
class Reality2:
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Private attributes
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    __graphql_http_url: str
    __graphql_webs_url: str
    __secure: bool
    __verify_ssl: bool

    __event_flags = []
    __event_threads = []
    __websockets = []
    __lock = None  # Thread safety lock
    # --------------------------------------------------------------------------------------------------------------------------------------------------


    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Constructor
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__ (self, domain_name, port, ssl = True, verify_ssl = True):
        self.__secure = ssl
        self.__verify_ssl = verify_ssl if ssl else False
        self.__lock = threading.Lock()
        self.__event_flags = []
        self.__event_threads = []
        self.__websockets = []

        if (ssl):
            self.__graphql_http_url = "https://" + domain_name + ":" + str(port) + "/reality2"
            self.__graphql_webs_url = "wss://" + domain_name + ":" + str(port) + "/reality2/websocket"
        else:
            self.__graphql_http_url = "http://" + domain_name + ":" + str(port) + "/reality2"
            self.__graphql_webs_url = "ws://" + domain_name + ":" + str(port) + "/reality2/websocket"

        logger.info(f"Reality2 client initialized: {self.__graphql_http_url}")
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Close all connections and cleanup resources
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def close(self, timeout=5.0):
        """Close all subscriptions and cleanup resources.

        Args:
            timeout: Maximum time to wait for threads to finish (seconds)
        """
        logger.info("Closing Reality2 client...")

        with self.__lock:
            # Signal all threads to stop
            for flag in self.__event_flags:
                flag.set()

            threads_to_join = list(self.__event_threads)
            websockets_to_close = list(self.__websockets)

        # Wait for threads to finish (with timeout)
        for thread in threads_to_join:
            if thread.is_alive():
                thread.join(timeout=timeout)
                if thread.is_alive():
                    logger.warning(f"Thread {thread.name} did not terminate within {timeout}s")

        # Close websockets
        for ws in websockets_to_close:
            try:
                ws.close()
                logger.debug("Websocket closed")
            except Exception as e:
                logger.error(f"Error closing websocket: {e}")

        with self.__lock:
            self.__event_flags.clear()
            self.__event_threads.clear()
            self.__websockets.clear()

        logger.info("Reality2 client closed")
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Context manager support
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Destructor - Close the connection(s)
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __del__ (self):
        pass
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    
    
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Public GraphQL methods
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Queries
    def sentantAll (self, passthrough = {}, details = "id name"):   
        return {**passthrough, **self.__graphql_post(self.__sentant_all(details), {})}

    
    def sentantGet (self, id="", passthrough = {}, details = "id name"):
        return {**passthrough, **self.__graphql_post(self.__sentant_get_by_id(details), {"id": id})}
        
    def sentantGetByName (self, name = "", passthrough = {}, details = "id name"):
        return {**passthrough, **self.__graphql_post(self.__sentant_get_by_name(details), {"name": name})}   
    
    # Mutations
    def sentantLoad (self, definition, passthrough = {}, details = "id name"):
        return {**passthrough, **self.__graphql_post(self.__sentant_load(details), {"definition": definition})}
    
    def swarmLoad (self, definition, passthrough = {}, details = "id name"):
        return {**passthrough, **self.__graphql_post(self.__swarm_load(details), {"definition": definition})}
    
    def sentantSend (self, id, event, parameters = {}, passthrough = {}, details = "id name"):
        return self.__graphql_post(self.__sentant_send(details), {"id": id, "event": event, "parameters": json.dumps(parameters), "passthrough": json.dumps(passthrough)})
    
    def sentantSendByName (self, name, event, parameters = {}, passthrough = {}, details = "id name"):
        """Send an event to a Sentant by name.

        Args:
            name: Name of the Sentant
            event: Event name
            parameters: Event parameters
            passthrough: Passthrough data
            details: GraphQL fields to return

        Returns:
            Response data dict

        Raises:
            Reality2Error: If Sentant not found or send fails
        """
        try:
            response = self.sentantGetByName(name, {}, details="id")
            if "sentantGet" in response and response["sentantGet"] is not None:
                id = response["sentantGet"]["id"]
                return self.__graphql_post(
                    self.__sentant_send(details),
                    {"id": id, "event": event, "parameters": json.dumps(parameters), "passthrough": json.dumps(passthrough)}
                )
            else:
                logger.warning(f"Sentant '{name}' not found")
                raise Reality2ResponseError(f"Sentant '{name}' not found")
        except Reality2Error:
            raise
        except (KeyError, TypeError) as e:
            logger.error(f"Error sending to Sentant '{name}': {e}")
            raise Reality2ResponseError(f"Invalid response when sending to '{name}'") from e

    def sentantUnload (self, id, passthrough = {}, details = "id name"):
        return {**passthrough, **self.__graphql_post(self.__sentant_unload(details), {"id": id})}
    
    def sentantUnloadByName (self, name, passthrough = {}, details = "id name"):
        """Unload a Sentant by name.

        Args:
            name: Name of the Sentant
            passthrough: Passthrough data
            details: GraphQL fields to return

        Returns:
            Response data dict

        Raises:
            Reality2Error: If Sentant not found or unload fails
        """
        try:
            response = self.sentantGetByName(name, {}, details="id")
            if "sentantGet" in response and response["sentantGet"] is not None:
                result = self.__graphql_post(self.__sentant_unload(details), {"id": response["sentantGet"]["id"]})
                return {**passthrough, **result}
            else:
                logger.warning(f"Sentant '{name}' not found for unload")
                raise Reality2ResponseError(f"Sentant '{name}' not found")
        except Reality2Error:
            raise
        except (KeyError, TypeError) as e:
            logger.error(f"Error unloading Sentant '{name}': {e}")
            raise Reality2ResponseError(f"Invalid response when unloading '{name}'") from e

    def sentantUnloadAll (self, passthrough = {}):
        """Unload all Sentants.

        Args:
            passthrough: Passthrough data

        Returns:
            List of unload results

        Raises:
            Reality2Error: If retrieval or unload fails
        """
        try:
            sentants = self.sentantAll()
            results = []
            if "sentantAll" in sentants:
                for sentant in sentants["sentantAll"]:
                    try:
                        result = self.sentantUnload(sentant["id"], passthrough)
                        results.append(result)
                    except Reality2Error as e:
                        logger.warning(f"Failed to unload Sentant {sentant.get('id', 'unknown')}: {e}")
            return results
        except Reality2Error:
            raise
        except (KeyError, TypeError) as e:
            logger.error(f"Error unloading all Sentants: {e}")
            raise Reality2ResponseError("Invalid response when unloading all Sentants") from e
    
    # Subscriptions
    def awaitSignal (self, id, signal, callback=None, details="event parameters passthrough sentant { id name description }"):
        """Subscribe to a Sentant signal via WebSocket.

        Args:
            id: UUID of the Sentant
            signal: Signal name to subscribe to
            callback: Function to call when signal is received
            details: GraphQL fields to return

        Raises:
            Reality2ConnectionError: If websocket connection fails
        """
        newEvent = threading.Event()
        newThread = threading.Thread(
            target=self.__subscribe,
            args=(self.__graphql_webs_url, id, signal, callback, details, newEvent),
            daemon=True,
            name=f"Reality2-{id[:8]}-{signal}"
        )

        with self.__lock:
            self.__event_flags.append(newEvent)
            self.__event_threads.append(newThread)

        newThread.start()
        logger.debug(f"Started subscription thread for {id}|{signal}")
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

        
    
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Private methods
    # --------------------------------------------------------------------------------------------------------------------------------------------------

    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # A POST for using with GraphQL
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __graphql_post(self, query, variables):
        """Execute a GraphQL query via HTTP POST.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Response data dict

        Raises:
            Reality2ConnectionError: Connection failed
            Reality2TimeoutError: Request timed out
            Reality2ResponseError: Invalid response format
            Reality2GraphQLError: GraphQL returned errors
        """
        try:
            body = {
                "query": query,
                "variables": json.dumps(variables)
            }

            # Suppress SSL warnings only for this specific request if verify_ssl is False
            if not self.__verify_ssl:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", urllib3.exceptions.InsecureRequestWarning)
                    answer = requests.post(
                        self.__graphql_http_url,
                        data=body,
                        verify=self.__verify_ssl,
                        timeout=30.0
                    )
            else:
                answer = requests.post(
                    self.__graphql_http_url,
                    data=body,
                    verify=self.__verify_ssl,
                    timeout=30.0
                )

            response = answer.json()

            if answer.status_code == 200:
                if "errors" in response:
                    # Extract error message with more detail
                    errors = response["errors"]
                    if isinstance(errors, list) and len(errors) > 0:
                        error = errors[0]
                        if isinstance(error, dict):
                            error_msg = error.get("message", str(error))
                        else:
                            error_msg = str(error)
                    else:
                        error_msg = str(errors)

                    logger.error(f"GraphQL error: {error_msg}")
                    logger.debug(f"Full GraphQL error response: {response}")
                    raise Reality2GraphQLError(f"GraphQL error: {error_msg}")
                else:
                    return response["data"]
            else:
                logger.error(f"HTTP error {answer.status_code}: {response}")
                raise Reality2ResponseError(f"HTTP {answer.status_code}: {response}")

        except Reality2Error:
            # Re-raise our own exceptions
            raise
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise Reality2TimeoutError(f"Request to {self.__graphql_http_url} timed out") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection failed: {e}")
            raise Reality2ConnectionError(f"Failed to connect to {self.__graphql_http_url}") from e
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise Reality2ConnectionError(f"Request failed: {e}") from e
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Response parsing error: {e}")
            raise Reality2ResponseError(f"Invalid response format: {e}") from e
    # --------------------------------------------------------------------------------------------------------------------------------------------------

        
        
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Check the status of the websocket
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __check_status (self, message):
        message_dict = json.loads(message)
        if "payload" in message_dict:
            if "status" in message_dict["payload"]:
                if message_dict["payload"]["status"] == "ok":
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    # --------------------------------------------------------------------------------------------------------------------------------------------------



    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Define the heartbeat thread that keeps the websocket connection alive (to be called in it's own a thread)
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __heartbeat_thread (self, websocket, running: threading.Event):
        heartbeat = {
            "topic": "phoenix",
            "event": "heartbeat",
            "payload": {},
            "ref": 0
        }
        
        while not running.is_set():
            for i in range(30):
                time.sleep(1)
                if running.is_set(): break
            websocket.send(json.dumps(heartbeat))
    # --------------------------------------------------------------------------------------------------------------------------------------------------

 

    # --------------------------------------------------------------------------------------------------------------------------------------------------
    # Subscribe to the Node channel representing the sentant and signal
    # --------------------------------------------------------------------------------------------------------------------------------------------------
    def __subscribe (self, server, sentantid, signal, callback, details, running: threading.Event):
        """Subscribe to a Sentant signal via WebSocket.

        Args:
            server: WebSocket server URL
            sentantid: Sentant UUID
            signal: Signal name
            callback: Callback function
            details: GraphQL fields
            running: Event flag for stopping the subscription

        Raises:
            Reality2ConnectionError: If websocket connection fails
        """
        join_message = {
            "topic": "__absinthe__:control",
            "event": "phx_join",
            "payload": {},
            "ref": 0
        }

        subscribe = {
            "topic": "__absinthe__:control",
            "event": "doc",
            "payload": {
                "query": self.__await_signal(details),
                "variables": {
                    "id": sentantid,
                    "signal": signal
                }
            },
            "ref": 0
        }

        try:
            # Connect to the server, join the channel and subscribe to the sentant event
            if self.__secure:
                # Create the SSL context
                ssl_context = ssl.create_default_context()
                if not self.__verify_ssl:
                    ssl_context.check_hostname = False
                    ssl_context.verify_mode = ssl.CERT_NONE

                with connect(server, ssl_context=ssl_context) as websocket:
                    self.__after_connect(websocket, join_message, subscribe, sentantid, signal, callback, server, running)
            else:
                with connect(server) as websocket:
                    self.__after_connect(websocket, join_message, subscribe, sentantid, signal, callback, server, running)

        except Exception as e:
            logger.error(f"WebSocket subscription failed for {sentantid}|{signal}: {e}")
            if not isinstance(e, Reality2Error):
                raise Reality2ConnectionError(f"Failed to connect to websocket: {e}") from e
            raise
            
            
    def __after_connect(self, websocket, join_message, subscribe, sentantid, signal, callback, server, running: threading.Event):
        """Handle websocket connection after establishment.

        Args:
            websocket: WebSocket connection
            join_message: Phoenix channel join message
            subscribe: GraphQL subscription message
            sentantid: Sentant UUID
            signal: Signal name
            callback: Callback function
            server: Server URL
            running: Event flag for stopping

        Raises:
            Reality2ConnectionError: If join or subscribe fails
        """
        # Track this websocket for cleanup
        with self.__lock:
            self.__websockets.append(websocket)

        try:
            # Join the channel
            websocket.send(json.dumps(join_message))
            message = websocket.recv()
            if self.__check_status(message):
                logger.info(f"Joined: {server}")
            else:
                logger.error(f"Failed to join: {server}")
                raise Reality2ConnectionError(f"Failed to join channel on {server}")

            # Subscribe to the Sentant and event
            websocket.send(json.dumps(subscribe))
            message = websocket.recv()
            if self.__check_status(message):
                logger.info(f"Subscribed to {sentantid}|{signal}")
            else:
                logger.error(f"Failed to subscribe to {sentantid}|{signal}")
                raise Reality2ConnectionError(f"Failed to subscribe to {sentantid}|{signal}")

            # Start the heartbeat thread
            heartbeat_thread = threading.Thread(
                target=self.__heartbeat_thread,
                args=(websocket, running),
                daemon=True,
                name=f"Heartbeat-{sentantid[:8]}"
            )
            heartbeat_thread.start()

            # Listen for messages
            while not running.is_set():
                try:
                    message = websocket.recv()
                    message_json = json.loads(message)
                    payload = message_json["payload"]

                    if self.__check_status(message):
                        logger.debug("Heartbeat received")
                    else:
                        if "result" in payload:
                            data = payload["result"]["data"]
                            if callback:
                                try:
                                    callback(data)
                                except Exception as e:
                                    logger.error(f"Error in callback for {sentantid}|{signal}: {e}")
                        elif "errors" in payload:
                            logger.error(f"GraphQL error in subscription: {payload['errors']}")
                            if callback:
                                try:
                                    callback(payload["errors"])
                                except Exception as e:
                                    logger.error(f"Error in error callback for {sentantid}|{signal}: {e}")
                        else:
                            logger.debug(f"Received: {payload}")

                except Exception as e:
                    if running.is_set():
                        # Normal shutdown
                        break
                    logger.error(f"Error receiving websocket message: {e}")
                    break

        finally:
            # Remove websocket from tracking
            with self.__lock:
                if websocket in self.__websockets:
                    self.__websockets.remove(websocket)
    # --------------------------------------------------------------------------------------------------------------------------------------------------



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
        mutation SentantSend($id: UUID4!, $event: String!, $parameters: Json, $passthrough: Json) {
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

# ------------------------------------------------------------------------------------------------------------------------------------------------------
