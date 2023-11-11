import os
import shutil
import requests
from git import Repo
from colorama import init, Fore
import pyfiglet as pyg
import subprocess
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

def display_program_name():
    res = pyg.figlet_format("GPD", font="lean")
    print()
    print(f" \t{Fore.CYAN}{res}")

def search_github_repo(package_name):
    search_url = f'https://api.github.com/search/repositories?q={package_name}&sort=stars&order=desc'
    response = requests.get(search_url)

    if response.status_code == 200:
        repositories = response.json().get('items', [])
        return repositories
    else:
        print(f"{Fore.RED}Error: Unable to fetch repository information. Status Code: {response.status_code}")
    return []

def is_package_downloaded(download_folder, package_name):
    package_folder = os.path.join(download_folder, package_name)
    return os.path.exists(package_folder)

def install_requirements(package_folder):
    requirements_file = os.path.join(package_folder, 'requirements.txt')
    if os.path.exists(requirements_file):
        print(f"{Fore.YELLOW}Installing requirements for the package...")
        subprocess.run(['pip', 'install', '-r', requirements_file], check=True)
        print(f"{Fore.GREEN}Requirements installed successfully.")
    else:
        print(f"{Fore.YELLOW}No requirements.txt file found. Skipping installation.")

def download_repository(repo_url, download_folder, package_name):
    if is_package_downloaded(download_folder, package_name):
        print(f"{Fore.YELLOW}Request already satisfied. '{package_name}' is already downloaded.")
        return

    temp_folder = os.path.join(os.getcwd(), 'temp_clone')
    os.makedirs(temp_folder, exist_ok=True)

    try:
        with ThreadPoolExecutor() as executor:
            # Use concurrent.futures.ThreadPoolExecutor for parallel execution
            future = executor.submit(Repo.clone_from, repo_url, temp_folder, depth=1)
            future.result()  # Wait for the cloning to complete

        package_folder = os.path.join(download_folder, package_name)

        os.makedirs(package_folder, exist_ok=True)

        shutil.copytree(temp_folder, package_folder, dirs_exist_ok=True)

        print(f"{Fore.GREEN}Repository cloned successfully from {repo_url} to {package_folder}")

        install_requirements(package_folder)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
    finally:
        shutil.rmtree(temp_folder, ignore_errors=True)

if __name__ == "__main__":
    display_program_name()

    package_name = input(f"{Fore.WHITE}Enter the package name: ")

    repositories = search_github_repo(package_name)

    if repositories:
        selected_repo = repositories[0]
        repo_url = selected_repo['clone_url']

        download_folder = os.path.join(os.getcwd(), 'GPD')
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
            print(f"{Fore.GREEN}Created 'GPD' directory at {download_folder}")

        download_repository(repo_url, download_folder, package_name)
    else:
        print(f"{Fore.RED}No repositories found.")
