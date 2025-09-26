# ****************************************************************************************************
# Finite State Machine Definition
#
# Roy C. Davies, 2023
# ****************************************************************************************************
import threading
import time


# ----------------------------------------------------------------------------------------------------
# A Transition
# ----------------------------------------------------------------------------------------------------
class Transition:
    # ------------------------------------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------------------------------------
    _state = ""
    _event = ""
    _newstate = ""
    _actions = []

    # ------------------------------------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------------------------------------
    def __init__(self, state, event, newstate, actions = {}):
        self._state = state
        self._event = event
        self._newstate = newstate
        self._actions = actions
# ----------------------------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------------------------
# An Automation
# ----------------------------------------------------------------------------------------------------
class Automation:
    # ------------------------------------------------------------------------------------------------
    # Attributes
    # ------------------------------------------------------------------------------------------------
    _state = ""
    _transitions = []
    _eventqueue = []
    _running = False

    # ------------------------------------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------------------------------------
    def __init__(self):
        self._state = "start"

    # ------------------------------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------------------------------
    # Check for state + event match, and do the actions if a transition is triggered.
    def _do_it(self, event):
        for transition in self._transitions:
            if ((transition._state == self._state) and (transition._event == event)) or ((transition._state == "*") and (transition._event == event)):
                print (transition._state + " : " + event + " => " + transition._newstate)
                result = ""
                for action in transition._actions:
                    if hasattr(action, "__call__"):
                        result = action(result)
                    else:
                        result = action
                if (transition._newstate != "*"):
                    self._state = transition._newstate
               
                break  
            
    # Take a step in then FSM time - check for new events and see if a timed event has occured
    def _step(self):
        if (len(self._eventqueue) > 0):
            eventtuple = self._eventqueue.pop(0)
            event = eventtuple[0]
            seconds = eventtuple[1]
            
            if (seconds == 0):
                self._do_it(event)
            else:
                timer = threading.Timer(seconds, self._do_it, args=(event,))
                timer.start()
    
    # The main thread for the FSM
    def _mainthread(self):
        self._running = True
        while self._running:
            self._step()
            time.sleep(0.1)  # Delay for 0.1 second
    # ------------------------------------------------------------------------------------------------



    # ------------------------------------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------------------------------------
    # Add a Transition to the FSM
    def add(self, transition):
        self._transitions.append(transition)

    # Start the FSM going
    def go(self):
        FSMthread = threading.Thread(target=self._mainthread)
        FSMthread.start()
        self._eventqueue.append(("init", 1))
        
    # Stop the FSM
    def stop(self):
        self._running = False

    # Send an event to the FSM.  The 'seconds' field means it will happen in the future.
    def event(self, newevent, seconds=0):
        self._eventqueue.append((newevent, seconds))
# ----------------------------------------------------------------------------------------------------