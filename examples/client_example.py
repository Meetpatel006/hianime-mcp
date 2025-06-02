"""Example usage of the Anime MCP Client Library."""
import asyncio
import json
import sys
from typing import Optional

try:
    from src.client import AnimeClient, PrintOptions
except ImportError as e:
    print("Error: Failed to import client library. Make sure you have installed the package:")
    print("  pip install -e .")
    sys.exit(1)

async def save_to_file(data: dict, filename: str):
    """Save data to a JSON file with pretty formatting."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully saved data to {filename}")
    except Exception as e:
        print(f"\nError saving to file: {str(e)}")

async def interactive_search():
    """Interactive anime search and details viewer."""
    try:
        async with AnimeClient() as client:
            print("Initializing client...")
            await client.initialize()
            
            while True:
                try:
                    print("\n=== Anime Explorer ===")
                    print("1. View Homepage")
                    print("2. Get Anime Details")
                    print("3. Save Homepage Data")
                    print("4. Exit")
                    
                    choice = input("\nEnter your choice (1-4): ")
                    
                    if choice == "1":
                        print("\nFetching homepage data...")
                        home_data = await client.get_home_page()
                        
                        print("\nDisplay options:")
                        print("1. Show everything")
                        print("2. Spotlight animes only")
                        print("3. Trending animes only")
                        print("4. Genres only")
                        
                        display = input("Choose display option (1-4): ")
                        
                        if display == "1":
                            client.print_homepage(home_data)
                        elif display == "2":
                            if home_data.get("spotlight_animes"):
                                print("\n=== Spotlight Animes ===")
                                for anime in home_data["spotlight_animes"]:
                                    print(f"\n- {anime['name']} ({anime['jname']})")
                                    print(f"  Type: {anime['type']}")
                                    if anime['episodes'].get('sub') or anime['episodes'].get('dub'):
                                        print(f"  Episodes: Sub={anime['episodes'].get('sub', 'N/A')}, "
                                              f"Dub={anime['episodes'].get('dub', 'N/A')}")
                            else:
                                print("\nNo spotlight animes found.")
                        elif display == "3":
                            if home_data.get("trending_animes"):
                                print("\n=== Trending Animes ===")
                                for anime in home_data["trending_animes"]:
                                    print(f"- {anime['name']} (Rank: {anime['rank']})")
                            else:
                                print("\nNo trending animes found.")
                        elif display == "4":
                            if home_data.get("genres"):
                                print("\n=== Available Genres ===")
                                print(", ".join(home_data["genres"]))
                            else:
                                print("\nNo genres found.")
                        else:
                            print("\nInvalid display option.")
                    
                    elif choice == "2":
                        anime_id = input("\nEnter anime ID (e.g., 'spy-x-family'): ")
                        if not anime_id.strip():
                            print("\nError: Anime ID cannot be empty")
                            continue
                            
                        print(f"\nFetching details for {anime_id}...")
                        
                        try:
                            details = await client.get_anime_details(anime_id)
                            if details["success"]:
                                # Configure display options
                                options = PrintOptions(
                                    show_description=input("\nShow description? (y/n): ").lower() == 'y',
                                    max_description_length=int(input("Max description length (default 200): ") or "200"),
                                    show_stats=input("Show stats? (y/n): ").lower() == 'y',
                                    show_genres=input("Show genres? (y/n): ").lower() == 'y',
                                    show_recommendations=input("Show recommendations? (y/n): ").lower() == 'y'
                                )
                                
                                info = details["data"]["anime"]["info"]
                                client.print_anime_info(info, options)
                                
                                # Additional information based on options
                                if options.show_genres and details["data"]["anime"]["moreInfo"]["genres"]:
                                    print("\nGenres:", ", ".join(details["data"]["anime"]["moreInfo"]["genres"]))
                                
                                if options.show_recommendations and details["data"].get("recommendedAnimes"):
                                    print("\nRecommended Animes:")
                                    for rec in details["data"]["recommendedAnimes"][:5]:  # Show top 5
                                        print(f"- {rec['name']}")
                            else:
                                print("Error: Failed to fetch anime details")
                        except Exception as e:
                            print(f"Error getting anime details: {str(e)}")
                    
                    elif choice == "3":
                        print("\nFetching homepage data to save...")
                        home_data = await client.get_home_page()
                        
                        filename = input("Enter filename to save (default: homepage.json): ").strip() or "homepage.json"
                        await save_to_file(home_data, filename)
                    
                    elif choice == "4":
                        print("\nGoodbye!")
                        break
                    
                    else:
                        print("\nInvalid choice. Please try again.")
                    
                    input("\nPress Enter to continue...")
                
                except KeyboardInterrupt:
                    print("\nOperation cancelled by user.")
                    continue
                except Exception as e:
                    print(f"\nError during operation: {str(e)}")
                    continue

    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        return 1

if __name__ == "__main__":
    try:
        asyncio.run(interactive_search())
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
        sys.exit(1)
