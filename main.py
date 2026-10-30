import streamlit as st
import plotly.graph_objects as go
import requests

st.title("Steam Data App")
steam_key = st.secrets["STEAM_API_KEY"]
steam_id = st.secrets["STEAM_ID"]

url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"


params = {
    'key': steam_key,
    'steamids': steam_id
}

overview, dataDispaly, chart = st.tabs(["Overview", "Top Games", "Chart"])
response = requests.get(url, params=params)

with overview:
    steam_id = st.text_input("Enter a steam ID number or profile link to display content:")

    if steam_id: # Note: IF USER INPUT
        if len(steam_id) > 17 and "https://steamcommunity.com/profiles/" in steam_id:
            steam_id = steam_id[-17:]

        try:

            steam_id = int(steam_id)
        except ValueError:
            st.warning("The entered value could not be converted into a number. "
                       "Please type in a valid 17-digit ID.")

        params = {
            'key': steam_key,
            'steamids': steam_id
        }
        response = requests.get(url, params=params)

        if response.status_code == 200:  # if response is OK
            data = response.json()
            players = data.get("response", {}).get("players", [])

            if players:
                player_info = players[0]

                avatar_url = player_info["avatarfull"]

                st.text("Player name: ")
                st.subheader(player_info.get("personaname", "Unknown Player"))
                player_name = player_info.get("personaname", "Unknown Player")

                st.image(avatar_url, width=256)

                match player_info.get("personastate"):

                    case 0:
                        st.info(f"{player_name} is currently OFFLINE or has a restricted profile")
                    case 1:
                        st.success(f"{player_name} is currently ONLINE! Go say hi!")
                    case _:
                        st.warning(f"Could not get status info of {player_name}.")
                try:
                    playtime_response = requests.get(
                        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/",
                        params={
                            "key": steam_key,
                            "steamid": steam_id,
                            "include_played_free_games": True
                        },
                        timeout=10
                    )
                    playtime_response.raise_for_status()
                    owned_games = (
                        playtime_response.json()
                        .get("response", {})
                        .get("games", [])
                    )
                    total_minutes = sum(
                        game.get("playtime_forever", 0)
                        for game in owned_games
                    )
                    total_hours = total_minutes / 60
                    total_days = total_hours / 24
                    total_years = total_days / 365
                except requests.exceptions.RequestException:
                    pass
                st.info(f"{player_name} has played for a total of {total_hours:.1f} hours / {total_days:.1f} days / {total_years:.1f} years")

    else:
        steam_id = st.secrets["STEAM_ID"]
        if response.status_code == 200:  # if response is OK
            data = response.json()
            players = data.get("response", {}).get("players", [])

            if players:
                player_info = players[0]

                avatar_url = player_info["avatarfull"]

                st.subheader("User:")
                st.subheader(player_info.get("personaname", "Unknown Player"))
                player_name = player_info.get("personaname", "Unknown Player")

                st.image(avatar_url, width=256)

                match player_info.get("personastate"):

                    case 0:
                        st.info(f"{player_name} is currently OFFLINE or has a restricted profile")
                    case 1:
                        st.success(f"{player_name} is currently ONLINE! Go say hi!")
                    case _:
                        st.warning(f"Could not get status info of {player_name}.")

                try:
                    playtime_response = requests.get(
                        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/",
                        params={
                            "key": steam_key,
                            "steamid": steam_id,
                            "include_played_free_games": True
                        },
                        timeout=10
                    )
                    playtime_response.raise_for_status()
                    owned_games = (
                        playtime_response.json()
                        .get("response", {})
                        .get("games", [])
                    )
                    total_minutes = sum(
                        game.get("playtime_forever", 0)
                        for game in owned_games
                    )
                    total_hours = total_minutes / 60
                    total_days = total_hours / 24
                    total_years = days / 365
                except requests.exceptions.RequestException:
                    pass
                st.info(f"{player_name} has played for a total of {total_hours} hours / {total_days:.0f} days / {total_years:.0f} years")


games = []
with dataDispaly:
    games_url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"

    games_params = {
        "key": steam_key,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": False
    }
    try:
        games_response = requests.get(
            games_url,
            params=games_params,
            timeout=10
        )
        games_response.raise_for_status()
        games_data = games_response.json()
        games = games_data.get("response", {}).get("games", [])


        st.subheader("How many games do you want to display?")
        quantity = st.slider(label = "Games to display:", min_value = 1 , max_value = 20, value = 5)

        # Sort by total playtime, highest first
        top_games = sorted(
            games,
            key=lambda game: game.get("playtime_forever", 0),
            reverse=True
        )[:quantity]

        if not top_games:
            st.info(
                "No games found. Check that your Steam game "
                "details are public."
            )
        else:
            # Column headers
            st.divider()
            rank_col, image_col, name_col, playtime_col, store_col = st.columns(
                [2, 6, 4, 2, 4]
            )

            rank_col.markdown("**Ranking**")
            image_col.markdown("**Game Image**")
            name_col.markdown("**Name**")
            playtime_col.markdown("**Playtime**")
            store_col.markdown("**Store Page**")

            st.divider()


            # Display each game as a row
            for rank, game in enumerate(top_games, start=1):
                app_id = game["appid"]
                game_name = game.get("name", "Unknown Game")
                hours = game.get("playtime_forever", 0) / 60

                image_url = (
                    f"https://cdn.akamai.steamstatic.com/steam/apps/"
                    f"{app_id}/header.jpg"
                )

                rank_col, image_col, name_col, playtime_col, store_col = st.columns(
                    [2, 6, 4, 2, 4]
                )

                rank_col.write(f"#{rank}")
                image_col.image(image_url, use_container_width=True)
                name_col.write(f"**{game_name}**")
                playtime_col.write(f"{hours:,.1f} hours")

                store_col.link_button(
                    "View Game",
                    f"https://store.steampowered.com/app/{app_id}"
                )

                st.divider()

    except requests.exceptions.RequestException as e:
        st.error(f"Could not retrieve games: {e}")

with chart:
    if not games:
        st.info("No game data is available to chart.")
    else:
        st.subheader("Playtime Visualization")

        chart_quantity = st.slider(
            "Number of games to chart:",
            min_value=1,
            max_value=min(20, len(games)),
            value=min(5, len(games)),
            key="chart_quantity"
        )

        chart_games = sorted(
            games,
            key=lambda game: game.get("playtime_forever", 0),
            reverse=True
        )[:chart_quantity]

        game_names = [
            game.get("name", "Unknown Game")
            for game in chart_games
        ]

        playtime_hours = [
            game.get("playtime_forever", 0) / 60
            for game in chart_games
        ]

        highest_playtime = max(playtime_hours)

        figure = go.Figure(
            data=[
                go.Bar(
                    x=game_names,
                    y=playtime_hours,
                    name="Hours Played per Game",
                    marker={
                        "color": playtime_hours,
                        "colorscale": [
                            [0, "#ff96cb"],
                            [1, "#4793d1"]
                        ],
                        "cmin": 0,
                        "cmax": highest_playtime or 1,
                        "showscale": False,
                        "colorbar": {
                            "title": "Hours"
                        }
                    }
                )
            ]
        )

        figure.update_layout(
            title=f"Top {chart_quantity} Steam Games by Playtime",
            xaxis_title="Game",
            yaxis_title="Playtime (Hours)",
            legend_title="Measurement",
            showlegend=True
        )

        st.plotly_chart(figure, use_container_width=True)
