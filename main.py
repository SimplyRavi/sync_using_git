import os
import subprocess
import json
import requests
import urllib.request
import time


# Check if Git is installed
def install_git():
    print("installing Git........................")
    url = "https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe"
    urllib.request.urlretrieve(url, "git_installer.exe")

    # Install Git
    os.system("git_installer.exe /VERYSILENT /NORESTART")
    os.remove("git_installer.exe")
    print("installation done")


def read_config():  
    # Read the config file
    with open('config.txt', 'r') as f:
        config = dict(line.strip().split('=') for line in f)
    print(config)
    return config


def is_changed(path, initial_timestamps):
    flag = False
    # Store the initial timestamps of the files in the directory
    # print("Intial ", initial_timestamps)
    current_timestamps = {}
    for filename in os.listdir(path):
        current_timestamps[filename] = os.stat(os.path.join(path, filename)).st_mtime
    # print(current_timestamps)

    # Compare the initial and current timestamps
    for filename in current_timestamps:
        if filename == '.git':
            pass
        else:
            if filename not in initial_timestamps:
                flag = True
                break
            elif current_timestamps[filename] != initial_timestamps[filename]:
                flag = True
                break

    initial_timestamps = current_timestamps

    return flag, initial_timestamps
        


def create_repository(repo_name, username, token):
    # Create the repository
    url = f"https://api.github.com/user/repos"
    data = json.dumps({'name': repo_name, 'private': True})
    headers = {'Content-Type': 'application/json', 'Authorization': f'token {token}'}
    response = requests.post(url, data=data, headers=headers)
    print(response.status_code)

    # Initialize the local repository and add the GitHub repository as a remote
    os.system(f'git init && git remote add origin https://github.com/{username}/{repo_name}.git')

    # Add and commit the files in the local repository
    os.system('git add . && git commit -m "Initial commit"')

    # Push the local repository to GitHub
    os.system('git push -u origin master')

    # here you can add a loop that keep watching changes on the local repo and updates the remote as well.


def git_repo(repo_name, username, token):
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        create_repository(repo_name, username, token)
    else:
        print("The repository already exists.")


try:
    git_installed = subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(git_installed.returncode)
    if git_installed.returncode != 0:
        # Download the installer
        install_git()
    else:
        print("Git is already installed.")
        # Set variables for the repository name, your GitHub username, and your personal access token
        try:
            config = read_config()
            repo_name = config['repo_name']
            username = config['username']
            token = config['token']
            folder = config['folder']
            os.chdir(folder)
            git_repo(repo_name, username, token)
            initial_timestamps = {}
            for filename in os.listdir(folder):
                initial_timestamps[filename] = os.stat(os.path.join(folder, filename)).st_mtime
            while True:
                flag, initial_timestamps = is_changed(folder, initial_timestamps)
                if flag:
                    os.system('git add .')
                    os.system('git commit -m "Auto-commit"')
                    os.system('git push -u origin master')
                time.sleep(5)
        except FileNotFoundError:
            print("Please make sure the config.txt file is present in the folder and the folder mentioned in config.txt to keep track of changes is there")
except FileNotFoundError:
    install_git()
except Exception as e:
    print(e.with_traceback())

