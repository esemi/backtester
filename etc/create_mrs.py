import os.path
import sys

from github import Github, Auth


def main(base_branch: str, token: str, from_num: int, to_num: int) -> None:
    auth = Auth.Token(token)
    g = Github(auth=auth)
    for number in range(from_num, to_num + 1):
        username = f'trader{number}'

        os.system('git checkout master')
        os.system(f'git checkout -b {username}')
        os.system(f"sed -i 's/USER_NAME/{username}/g' .github/workflows/deploy.yml")
        os.system('git add .github/workflows/deploy.yml')
        os.system(f'git commit -m "WIP: {username}"')
        os.system(f'git push -u origin {username}')

        # create MR with label rebase
        repo = g.get_repo('esemi/backtester')
        pull_request = repo.create_pull(
            title=f'WIP: {username}',
            head=username,
            base=base_branch,
        )
        pull_request.add_to_labels('rebase')
        print(pull_request)

    g.close()


# Usage: `python etc/create_mrs.py PAT_TOKEN_HERE 101 200 release-pool-2`
if __name__ == '__main__':
    main(sys.argv[4], sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
