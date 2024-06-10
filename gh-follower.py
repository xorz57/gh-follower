import os
import csv
import requests
import time
import click
from requests.auth import HTTPBasicAuth

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

GITHUB_API_URL = "https://api.github.com"


def get_following_users():
    users = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/user/following"
        auth = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)
        params = {"page": page, "per_page": 100}
        response = requests.get(url, auth=auth, params=params)
        if response.status_code == 200:
            current_page_users = response.json()
            if not current_page_users:
                break
            users.extend(current_page_users)
            page += 1
        else:
            click.echo(f"Failed to retrieve following users!")
            break
    return users


def get_org_members(org):
    members = []
    page = 1
    while True:
        url = f"{GITHUB_API_URL}/orgs/{org}/members"
        auth = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)
        params = {"page": page, "per_page": 100}
        response = requests.get(url, auth=auth, params=params)
        if response.status_code == 200:
            current_page_members = response.json()
            if not current_page_members:
                break
            members.extend(current_page_members)
            page += 1
        else:
            click.echo(f"Failed to retrieve members of {org}!")
            break
    return members


def save_csv(users, filename):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Username", "URL"])
        for user in users:
            writer.writerow([user["login"], user["html_url"]])
    click.echo(f"Successfully saved to {filename}!")


def load_csv(filename):
    users = []
    with open(filename, "r") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            users.append(row)
    return users


def follow_user(username):
    url = f"{GITHUB_API_URL}/user/following/{username}"
    auth = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)
    response = requests.put(url, auth=auth)
    if response.status_code == 204:
        # click.echo(f"Successfully followed {username}!")
        pass
    else:
        click.echo(f"Failed to follow {username}!")


def unfollow_user(username):
    url = f"{GITHUB_API_URL}/user/following/{username}"
    auth = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)
    response = requests.delete(url, auth=auth)
    if response.status_code == 204:
        # click.echo(f"Successfully unfollowed {username}!")
        pass
    else:
        click.echo(f"Failed to unfollow {username}!")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("filename")
def export_following_users_to_csv(filename):
    users = get_following_users()
    save_csv(users, filename)


@cli.command()
@click.argument("org")
@click.argument("filename")
def export_org_members_to_csv(org, filename):
    users = get_org_members(org)
    save_csv(users, filename)


@cli.command()
@click.argument("filename")
@click.option(
    "-d", "--delay", default=30, help="Delay between follow requests in seconds"
)
def follow_users_from_csv(filename, delay):
    users = load_csv(filename)
    with click.progressbar(users, label="Following users") as bar:
        for user in bar:
            username = user["Username"]
            follow_user(username)
            time.sleep(delay)


@cli.command()
@click.argument("filename")
@click.option(
    "-d", "--delay", default=5, help="Delay between unfollow requests in seconds"
)
def unfollow_users_from_csv(filename, delay):
    users = load_csv(filename)
    with click.progressbar(users, label="Unfollowing users") as bar:
        for user in bar:
            username = user["Username"]
            unfollow_user(username)
            time.sleep(delay)


@cli.command()
@click.argument("org")
@click.option(
    "-d", "--delay", default=30, help="Delay between follow requests in seconds"
)
def follow_org_members(org, delay):
    users = get_org_members(org)
    with click.progressbar(users, label=f"Following members of {org}") as bar:
        for user in bar:
            username = user["login"]
            follow_user(username)
            time.sleep(delay)


@cli.command()
@click.argument("org")
@click.option(
    "-d", "--delay", default=5, help="Delay between unfollow requests in seconds"
)
def unfollow_org_members(org, delay):
    users = get_org_members(org)
    with click.progressbar(users, label=f"Unfollowing members of {org}") as bar:
        for user in bar:
            username = user["login"]
            unfollow_user(username)
            time.sleep(delay)


if __name__ == "__main__":
    cli()
