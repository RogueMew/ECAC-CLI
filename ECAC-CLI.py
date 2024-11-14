#Custom Modules 
import Modules.ECAC as ECAC
import Modules.fortniteTrackerSccraper as FTS
import Modules.valorantTrackerScraper as VTS

#Installed Modules
import typer
import os
import json

class CustomError(Exception):
    def __init__(self, message:str) -> None:
        self.message = message
    
    def __str__(self) -> str:
        return self.message
    
app = typer.Typer()

def read_file(api_key_path: str) -> str:
    try:
        file = open(f"{api_key_path}", "r")
        output = file.readline()
        return output
    
    except Exception as e:
        print(f"Error:\n{e}")

def get_key(api_key_path:str) -> str:
    if os.path.isfile(api_key_path) is False:
        raise CustomError(f"File Doesnt Exist: {api_key_path}")
    if api_key_path.endswith(".txt") is False:
        raise CustomError("API key file must be a .txt file")
    
    key = read_file(api_key_path)
    
    if not key.startswith("Bearer"):
        raise CustomError("Incorrect API Key, Must start with Bearer")
    return key

def check_output_folder(output_folder: str) -> None:
    if os.path.isdir(output_folder) is False:
        os.mkdir(f"./{output_folder}")

@app.command()
def scrape_users(api_key_path: str, comp_id: int, network: str, bracket_id: int = None, output_folder: str = "Output"):
    
    #Check Vars
    check_output_folder(output_folder)
    
    #Set ECAC Vars
    ECAC.ECAC_API_header.set(get_key(api_key_path))
    ECAC.comp_details.set_id(comp_id)
    ECAC.network = network
    
    #Run ECAC Comp Details Scrape
    ECAC.comp_details.scrape_details()
    
    #Actual Processor
    file = open(f"./{output_folder}/{ECAC.comp_details.read()['name'].replace(" ", "-")}-users.json", "w", encoding="utf-8")
    
    if bracket_id is None:
        file.write(json.dumps(ECAC.process_contact_info(ECAC.scrape_team_ids()), ensure_ascii=False))
        file.close()
    else:
        file.write(json.dumps(ECAC.process_contact_info(ECAC.scrape_team_ids_bracket(bracket_id)), ensure_ascii=False))
        file.close()

@app.command()
def fortnite_stats(api_key_path: str, comp_id: int, mode: str = "BR", team_stats: bool = False, peak_rank:bool = False, current_rank: bool = False, output_folder: str = "Output", bracket_id: int = None) -> None:
    #Check Vars    
    check_output_folder(output_folder)
    
    #set ECAC Vars
    ECAC.ECAC_API_header.set(get_key(api_key_path))
    ECAC.comp_details.set_id(comp_id)
    ECAC.network ="EPIC"
    ECAC.comp_details.scrape_details()
    
    if not peak_rank and not current_rank:
        raise CustomError("Missing Parameters for Ranks Wanted: Peak and/or Current Rank")
    
    if team_stats:
        if peak_rank:
            FTS.scrape_peak_team_average(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), file_name=ECAC.comp_details.read()["name"].replace(" ", "-")+"-peak-team-avrerage", output_folder=output_folder, mode= "Br" if mode != "ZB" else "ZB")
        if current_rank:
            FTS.scrape_current_team_average(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), file_name=ECAC.comp_details.read()["name"].replace(" ", "-")+"-current-team-average", output_folder=output_folder, mode= "BR" if mode != "ZB" else "ZB")
    else:
        if peak_rank:
            FTS.scrape_peak_rank(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), file_name=ECAC.comp_details.read()["name"].replace(" ", "-")+"-current-rank", output_folder=output_folder)
        if current_rank:
            FTS.scrape_current_rank(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), file_name=ECAC.comp_details.read()["name"].replace(" ", "-")+"-current-rank", output_folder=output_folder)

@app.command()
def valorant_stats(api_key_path:str, comp_id: int, team_stats: bool = False, peak_rank: bool = True, current_rank: bool = False, output_folder: str = "Output", bracket_id: int = None) -> None:
    
    #Check Vars
    check_output_folder(output_folder)
    
    #Set ECAC Vars
    ECAC.ECAC_API_header.set(get_key(api_key_path))
    ECAC.comp_details.set_id(comp_id)
    ECAC.network = "RIOT"
    ECAC.comp_details.scrape_details()
    
    if not peak_rank and not current_rank:
        raise CustomError("Missing Parameters for Ranks Wanted: Peak and/or Current Rank")
    
    if team_stats:
        if current_rank:
            VTS.scrape_current_team_average(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), ECAC.comp_details.read()["name"].replace(" ", "-")+"-current-team-average", output_folder)
        
        if peak_rank:
            raise CustomError("Peak Rank is not Currently Supported")
    else:
        if current_rank:
            VTS.scrape_current_rank(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), ECAC.comp_details.read()["name"].replace(" ", "-")+"-current-rank", output_folder)
        
        if peak_rank:
            VTS.scrape_peak_rank(ECAC.process_contact_info(ECAC.scrape_team_ids() if bracket_id is None else ECAC.scrape_team_ids_bracket(bracket_id)), ECAC.comp_details.read()["name"].replace(" ", "-")+"-peak-rank", output_folder)
    
    

if __name__ == "__main__":
    app()