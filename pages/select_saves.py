from elements.message import message
import elements.theme as theme
from nicegui import app, ui
from handlers.savehandler import *
import traceback

# call the function to pull in that info of the saves.
@ui.page('/selectsaves/')
async def view_saves():
    with theme.frame('View Saves'):
        # File path for save data
        selected_game = app.storage.user.get("selected_game", {})
        # Get the paths
        user_config = app.storage.user.get("config", {})
        paths = user_config.get("Paths",{})
        root_path = paths.get("osrootpath")
        games_path = paths.get("gamespath", "Not Set")
        saves_path = paths.get("savespath", "Not Set")

        def load_save_from_storage(existing_saves, selected_save_name):
            for name in selected_save_name:
                selected_save = {}
                save_to_get = convert_save_name(name)
                try:
                    selected_save = existing_saves[save_to_get]
                    app.storage.user['is_save_loaded']  = True
                except:
                    ui.notify("Unable to load save.", type='negative', position="top",)
                finally:
                    # pass back empty dict even if nothing is available.
                    app.storage.user["selected_save"] = selected_save
                    ui.navigate.reload()

        async def render_save_cards(existing_saves, save):
            with ui.card().tight().style('width: 100%; max-width: 250px; aspect-ratio: 4 / 3; max-height: 175px;'):
                with ui.card_section():
                    ui.label().bind_text_from(save, 'name', backward=lambda name: f'{name}')
                    ui.label().bind_text_from(save, 'base_game',
                                                            backward=lambda base: f'Base Game: {base}')
                    ui.label().bind_text_from(save, 'create_date',
                                                            backward=lambda create: f'Start Date: {create}')
                    ui.label().bind_text_from(save, 'date_last_save',
                                                            backward=lambda last_save: f'Last Save: {last_save}')
                    with ui.card_actions().classes("w-full justify-end"):
                        ui.button('Select Save', on_click=lambda: load_save_from_storage(existing_saves, {save['name']}))

        # No game selected
        if not selected_game or 'name' not in selected_game:
            with ui.row():
                ui.icon('warning').classes('text-3xl')
                ui.label('Warning: No selected game detected.').classes('text-2xl')
            ui.label('Cannot view the saves for a game with no game selected.')
            ui.label('Please select a game from \'View Games\'.')
            ui.label('Then return here to view the save files.')
            with ui.link(target = '/selectgames'):
                ui.button('Find Game File')
        # There IS a selected_game
        else:
            try:
                # Getting the games
                str_games_path = root_path + games_path
                # formatting the game name
                game_format_result = format_str_for_filename_super(selected_game['name'])
                game_file_name = ''
                if game_format_result['result']:
                    game_file_name = game_format_result['string']
                else:
                    ui.notify("Error with formatting selected_game name.", position='top', type='warning')
                
                str_saves_path = str_games_path + '\\' + game_file_name + '\\' +  saves_path
                existing_saves = {}
                # getting the existing saves for the loaded game
                try:
                    existing_saves_result = get_saves(str_saves_path)
                    # If it doesnt' return a result_dict, we know we have the saves.
                    if existing_saves_result:
                        existing_saves = existing_saves_result
                    else:
                        ui.notify(f"""Error: Could not fetch saves for the game! Please check folder location.""",
                                  position='top',
                                  type='warning',
                                  multi_line=True)
                except Exception as e:
                    print(traceback.format_exc())
                    ui.notify(f"Error loading saves: {str(e)}", type='negative', position="top",)
                    return
                
                with ui.column().classes('items-center w-full gap-4 p-6 max-w-5xl'):
                    ui.label("When you selected a save the Selected Save in the bottom left corner will update.")
                    ui.label("Select a save to load:")

                with ui.link(target='/createsave'):
                    ui.button("Create New Save")
                with ui.link(target='/loadeddash'):
                    ui.button("Go to Dashboard")

            
                save_card_container = ui.row().classes("full flex items-center")
                with save_card_container:
                    if existing_saves:
                        for save in existing_saves.values():
                            await render_save_cards(existing_saves, save)
                    else:
                        ui.label("No saves to display!")
            except Exception as e:
                print(traceback.format_exc())
                ui.notify(f"""Save files could not be viewed..
                            Please check in console for traceback.""",
                            type='negative',
                            position='top',
                            multi_line = True)





