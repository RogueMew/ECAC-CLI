import requests as web
from tqdm import tqdm
import json

#Classes
class header:
    """
    Manages single header settings allowing easy configuration and retrieval
    """
    
    def __init__(self, headerTitle) -> None:
        """
        Creates Header Object with the Header Key Value as a Param

        Parameters:
            headerTitle (any): Header Key Value
        """
        
        self.header = {headerTitle : None}
        self.headerTitle = headerTitle 
        pass
    
    def set(self, headerValue) -> None:
        """
        Sets the Header Value as the input of this Function

        Parameters:
            headerValue (any): Value of the Header Key
        """
        
        self.header = {self.headerTitle : headerValue}
        pass
    
    def read(self) -> dict:
        """
        Returns a Dictionary of the Header
        
        Returns:
            dict: Header Values
        """
        
        return self.header

    def is_empty(self) -> bool:
        """
        Returns a Boolean indicating if the header is Not set.
        
        Returns:
            bool: True if the variable is None, False otherwise.
        """
        
        return self.header.get(self.headerTitle) is None

class CustomError(Exception):
    """
    Custom Error Message Class Allowing for Custom Errors
    """
    
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}"

class compDetails:
    """
    Class that handles the competition Values Such as Name, Id, and Size
    """
    
    def __init__(self) -> None:
        """
        Initializes a new instance of the compDetails class

        Attributes:
            data (dict): Dictionary that stores all the data pertaining to the Name, Id, and Size of a Competition
            url (str): String that contains the URL that is called to make requests
        """
       
        self.data = {}
        self.url = "https://api.ecac.gg/competition/{}"
        pass

    def set_id(self, id: int) -> None:
        """
        Sets the Id of the object
        
        Parameters:
            id (int): Id of the competition
        """

        self.data["id"] = id
        pass
    
    def is_empty(self, data_point: str="id") -> bool:
        """
        Checks to see if specified data point is empty(i.e., None)

        Parameters:
            data_point (str, optional):
                The key in the dictionary that is being checked.
                Defaults to "id" if not provided

        Returns:
            bool: True if the variable is None, False otherwise.

        Raises:
            CustomError: If `data_point` is not a valid key in the data dictionary.
        """
        
        if data_point not in list(self.data.keys()):
            raise CustomError(f"{data_point} is Not in List of Acceptable Parameters: {list(self.data.keys())}")
        return self.data.get(data_point) is None
    
    def scrape_details(self) -> None:
        """
        Scrapes the Competitions API Endpoint and Pulls Data such as Name and Size
        
        Raises:
            CustomError: If the competition ID is not set or if there is an error communicating with the server.
        """
        
        if self.is_empty():
            raise CustomError("Id is not set and is a needed for any requests")
        request = web.get(self.url.format(self.data["id"], 1))
        if request.status_code != 200:
            raise CustomError(f"Error Communicating with Server, Error Code: {request.status_code} ")
       
        self.data["name"] = json.loads(request.text).get("name", None)
        self.data["size"] = json.loads(request.text).get("totalElements", None)
    
    def read(self, name: bool=True, id: bool=True, size: bool=True) -> dict:
        """
        Retrieves the competition data as a dictionary, with options to include or exclude specific details.

        Parameters:
            name (bool, optional): If `True`, includes the competition name in the result. Defaults to `True`.
            id (bool, optional): If `True`, includes the competition ID in the result. Defaults to `True`.
            size (bool, optional): If `True`, includes the competition size in the result. Defaults to `True`.

        Returns:
            dict: A dictionary containing the selected competition data. Keys will be "name", "id", and/or "size", based on the parameters.
        """
        
        result ={}
        if name:
            result["name"] = self.data.get("name", None)
        if id:
            result["id"] = self.data.get("id", None)
        
        if size:
            result["size"] = self.data.get("size", None)
        
        return result

#Header
ECAC_API_header = header("authorization")

#Classed Variables
comp_details = compDetails()
network = None

#Util
def is_empty(var: any) -> bool:

    
    return var is None

#Competition Functions
def get_team_name(team_id: int) -> str:
    return json.loads(web.get("https://api.ecac.gg/competition/entry/{}".format(team_id)).text).get("alternateName", f"{team_id}")      
    
def grab_comp_dict() -> dict:
    """
    Returns the API response for the selected competion based off Id

    Returns:
        dict: The competitions data as a python dictionary
    
    Raises:
        CustomError: When their is a Network Error or the competition site is empty
    """
    
    if comp_details.is_empty():
        raise CustomError("Competition ID is Empty")

    request = web.get("https://api.ecac.gg/competition/entry/document?competitionId={}&page=0&size=1000&sort=seed".format(comp_details.read(name=False, size=False)["id"]))

    if request.status_code != 200:
        raise CustomError(f"Request Error: {request.status_code}")

    if json.dumps(request.text) == {}:
        raise CustomError("Empty Comp Site")

    return json.loads(request.text)

#Team Function

def confirm_assistant(id: int, assitant_id: list) -> bool:
     if id in assitant_id:
         return True
     else:
         return False
     
#Bracket Functions
def grab_bracket_dict(bracket_id: int) -> dict:
    """
    Returns the API response for the selected bracket based off Id

    Parameters:
        bracket_id (int): Bracket Id 

    Returns:
        dict: Bracket data as a python dict
    
    Raises:
        CustomError: When their is a Network Error or the competition site is empty
    """
    
    if comp_details.is_empty():
        raise CustomError("Competition ID is not Set")
    request = web.get("https://api.ecac.gg/competition/entry/document?competitionId={}&brackets={}&page=0&size=2000".format(comp_details.read(name=False, size=False)["id"], bracket_id))

    if request.status_code != 200:
        raise CustomError(f"Request Error: {request.status_code}")

    if json.dumps(request.text) == {}:
        raise CustomError("Empty Bracket Site")
    
    return json.loads(request.text)
    
def scrape_team_ids_bracket(bracket_id: int) -> list:
    """
    Parses the bracket data and returns the team ids

    Parameters:
        bracket_id (int): Bracket Id

    Returns:
        list: A List containing team ids

    Raises:
        CustomError: If a vital key in the JSON is missing the program will raise an error
    """
    
    bracket_contents = grab_bracket_dict(bracket_id)
    team_id_list = []
    if "content" not in list(bracket_contents.keys()):
        raise CustomError("Missing Data")
    for team in bracket_contents["content"]:
        team_id_list.append(team["id"])
    return team_id_list

#Gather and Scrape Funcs   
def scrape_team_ids() -> list:
    """
    Parses the competition data and returns the team ids
    
    Returns:
        list: Team Ids as a list    
    
    Raises:
        CustomError: If a Vital key is missing in the JSON
    """
    
    comp_contents = grab_comp_dict()
    team_id_list = []
    if "content" not in list(comp_contents.keys()):
        raise CustomError("Missing Data")
    for team in comp_contents["content"]:
        team_id_list.append(team["id"])
    return team_id_list

def get_team_contacts(teamIDS: list) -> list:
    """
    Scrapes the contact info of a team and returns all data in a list to be parsed

    Parameters:
        teamIDS (list): A list of team Ids
    Returns:
        list: Team contact info
    
    Raises:
        CustomError: If Header is empty, needs updating or Error incommunication with api
    """
    
    if ECAC_API_header.is_empty():
        raise CustomError("ECAC Header is not Set")

    team_contacts = []
    for id in tqdm(teamIDS, total=len(teamIDS), desc="Scraping Team Contacts Page", bar_format="{l_bar}{bar:30}{r_bar}"):
        request = web.get("https://api.ecac.gg/competition/entry/{}/_view/contact-accounts".format(id), headers=ECAC_API_header.read())
        if request.status_code != 200:
            if request.status_code == 401:
                raise CustomError("Request Header Needs Updating")
            else:
                raise CustomError(f"Error in Communication with API, Web Error Code {request.status_code}")
        team_contacts.append(request.text)
    return team_contacts

def process_contact_info(team_id_list: list) -> dict:
    """
    Parses the contact info and returns all info as a dictionary

    Parameters:
        team_id_list (list): A list of team Ids that correspond with the teams in the contact info list

    Returns:
        dict: Team contacts all orderly fashioned and stored by school name as key value
    """
    def process_contact_info_func(team_json: list, assistant_id: list = None) -> list:
        """
        Mini process Function
        """
        
        temp_dict = json.loads(team_json)
        user_id_list = []
        user_contacts = []
        if temp_dict != {}:
            for contacts in temp_dict["content"]:
                user_id_list.append(contacts["user"]["id"])

            user_id_list = list(set(user_id_list))

            for id in user_id_list:
                user_dict = {
                    "id" : None,
                    "game_network_username": None,
                    "discord" : None
                }
                for contacts in temp_dict["content"]:
                    if contacts["user"]["id"] == id:
                        user_dict["id"] = id
                        if contacts["network"] == network:
                            
                            user_dict["game_network_username"] = contacts["handle"]

                        elif contacts["network"] == "DISCORD":
                            user_dict["discord"] = contacts["handle"]    
                
                user_contacts.append(user_dict)
            return user_contacts
        
        else:
            user_dict = {"game_network_username" : "Empty Team", "discord" : "Empty Team"}
            user_contacts.append(user_dict)
            return user_contacts

    temp_dict = {}
    teams_contacts = get_team_contacts(team_id_list)
    
    for team in tqdm(teams_contacts, total= len(teams_contacts), desc= "Processing Teams", bar_format="{l_bar}{bar:30}{r_bar}"):
    #for team in teams_contacts:
        participant_id = []
        data = json.loads(web.get(f"https://api.ecac.gg/competition/entry/{team_id_list[teams_contacts.index(team)]}/members").text)
        if data.get("content", None) is None:
            continue
        for participant in data["content"]:
            participant_id.append(participant["participant"]["id"])
        

        temp_dict[get_team_name(team_id_list[teams_contacts.index(team)])] = process_contact_info_func(team)
    return temp_dict


# Grab Match Ids
def team_match_ids(team_id: int) -> list:
    """
    Scrapes the matches that are located on the teams page

    Parameters:
        team_id (int): Team Id
    
    Returns:
        list: list of match Ids
    
    Raises:
        CustomError: if there is an issue connecting to API
    """
    
    returned_list = []

    expandHeader = header("expand")
    expandHeader.set("_links,totalElements,content{bracket{settings},event,games,assignments{entry{leader,representing{additionalOrganizations}}}}")
    request = web.get("https://api.ecac.gg/competition/{}/_view/matches?entry={}&page=0".format(comp_details.read(name=False,size=False)["id"], team_id), headers=expandHeader.read())

    if request.status_code != 200:
        raise CustomError(f"Web Status Code: {request.status_code}")
    if request.json().get("content", None) == None:
        return returned_list
    
    for item in request.json()["content"]:
        returned_list.append(item["id"])
    
    return returned_list

def scrape_bracket_ids(competition_id: int) -> list:
    """
    Scrapes the bracket ids that are located in the competition page

    Parameters:
        competition_id (int): the Id of the competition in which the brackets are located
    """

    returned_list = []

    request = web.get("https://api.ecac.gg/competition/{}/brackets".format(competition_id))

    if request.status_code != 200:
        raise CustomError(f"Error Connecting with API, Web Error: {request.status_code}")
    
    if "content" not in list(json.loads(request.text).keys()):
        raise CustomError(f"Missing Vital key for Data")
    
    for bracket in json.loads(request.text)["content"]:
        returned_list.append(bracket.get("id"))

    return returned_list