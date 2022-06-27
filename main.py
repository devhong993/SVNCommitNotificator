import os
import sys
import logging
import json
import pathlib
import requests
from requests.structures import CaseInsensitiveDict

def main():

    try:

        current_path = pathlib.Path(__file__).parent.resolve()

        # Get SVN arguments from executed hook scripts command
        # Only works in Post-commit 
        args_list = sys.argv

        # Files
        f1 = open(args_list[1].replace('\\', '/'), "r", encoding='utf-8')
        s1 = f1.readlines()
        f1.close()

        svn_file_list = ""
        svn_file_cnt = 0
        for i in s1:
            svn_file_cnt += 1
            svn_file_list += i

        # Commit message
        f3 = open(args_list[3].replace('\\', '/'), "r", encoding='utf-8')
        s3 = f3.readlines()
        f3.close()

        svn_commit_msg = ""
        for i in s3:
            svn_commit_msg += i

        # Revision
        svn_revision = args_list[4]

        # ?
        #f5 = open(args_list[5].replace('\\', '/'), "r", encoding='utf-8')
        #s5 = f5.readlines()
        #f5.close()

        # Open and read local config
        local_config_path = os.path.join(current_path, 'local.config')
        with open(local_config_path, encoding='utf-8') as f_author:
            lines = f_author.readlines()

        # [AUTHOR] : author_name
        # [REPO_NAME] : repo_name
        # [USE_NOTIFY_SYSTEM] : true/false
        svn_author = ""
        svn_repo_name = ""
        use_notify_system = False
        for line in lines:
            local_config_line_data = line.split('=')
            if local_config_line_data[0] == "AUTHOR":
                svn_author = local_config_line_data[1].replace("\n", "")
            if local_config_line_data[0] == "USE_NOTIFY_SYSTEM":
                use_notify_system = local_config_line_data[1].lower() == "true"

        if svn_author == "":
            raise Exception("Cannot find author name!")

        if use_notify_system == False:
            return

        # Open and read hook config data
        hookinfo_config_path = os.path.join(local_config_path, 'hookinfo.config')
        with open(hookinfo_config_path, encoding='utf-8') as f_hook_config:
            lines = f_hook_config.readlines()

        # [REPO_NAME] : proj_name
        # [HOOK_TARGET] : DISCORD, MS_TEAMS
        # [HOOK_URL] : url_link
        hook_target = ""
        hook_url = ""
        for line in lines:
            hook_config_line_datas = line.split('=')
            if hook_config_line_datas[0] == "HOOK_TARGET":
                hook_target = hook_config_line_datas[1].strip()
            elif hook_config_line_datas[0] == "HOOK_URL":
                svn_repo_name = hook_config_line_datas[1].strip()
            elif hook_config_line_datas[0] == "REPO_NAME":
                hook_url = hook_config_line_datas[1].strip()

        if svn_repo_name == "":
            raise Exception("Cannot setup repository name!")

        if hook_target == "":
            raise Exception("HOOK_TARGET is empty!")

        if hook_url == "":
            raise Exception("HOOK_URL is empty!")

        # Send JSON data
        if hook_target == "DISCORD":
            SendToDiscordBot(svn_author, svn_repo_name, svn_revision, svn_file_cnt, svn_commit_msg, hook_url)
        elif hook_target == "MS_TEAMS":
            SendToMicrosoftTeams(svn_author, svn_repo_name, svn_revision, svn_file_cnt, svn_commit_msg, hook_url)
        else:
            print("HOOK_TARGET is wrong.")

        # TODO : Another type for webhook

    except:
        logging.exception('')
        return

    finally:
        return

def SendToDiscordBot(author, repo_name, revision, change_cnt, commit_log, url):

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {}
    if commit_log == "":
        data["content"] = "[%s] [%s] %s Commit:\n<No Comment>\nAffected file count : %i" % (repo_name, revision, author, change_cnt)
    else:
        data["content"] = "[%s] [%s] %s Commit:\n%s\nAffected file count : %i" % (repo_name, revision, author, commit_log, change_cnt)
    
    encoded_data = json.dumps(data, ensure_ascii=False).encode('utf8')
    requests.post(url, headers=headers, data=encoded_data)

    return

def SendToMicrosoftTeams(author, repo_name, revision, change_cnt, commit_log, url):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    data = {}
    if commit_log == "":
        data["text"] = "[%s] [%s] %s Commit:\n<No Comment>\nAffected file count : %i" % (repo_name,revision, author, change_cnt)
    else:
        data["text"] = "[%s] [%s] %s Commit:\n%s\nAffected file count : %i" % (repo_name,revision, author, commit_log, change_cnt)
    
    encoded_data = json.dumps(data, ensure_ascii=False).encode('utf8')
    requests.post(url, headers=headers, data=encoded_data)

    return

# Run
main()