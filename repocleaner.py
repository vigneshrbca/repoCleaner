import os
import json
from datetime import datetime, timedelta
from github import Github

token = os.getenv("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")  

TW_YEARS = 1  
TW_DAYS = TW_YEARS * 365

def get_stale_branches(repo):
    stale_branches = []
    all_branches = list(repo.get_branches())
    
    for branch in all_branches:
        commit_date = branch.commit.commit.author.date
        age = (datetime.utcnow() - commit_date.replace(tzinfo=None)).days
        if age > TW_DAYS:
            stale_branches.append((branch.name, age))
    
    return all_branches, stale_branches

def delete_branches(repo, branches):
    for branch in branches:
        try:
            ref = repo.get_git_ref(f"heads/{branch}")
            ref.delete()
            print(f"Deleted branch: {branch}")
        except Exception as e:
            print(f"Failed to delete branch {branch}: {e}")

def main():
    with open("masterRepoList.txt", "r") as f:
        repo_list = [line.strip().split("github.com/")[-1] for line in f if line.strip()]
    
    summary = {}
    
    for repo_name in repo_list:
        try:
            repo = g.get_repo(repo_name)
            all_branches, stale_branches = get_stale_branches(repo)
            summary[repo_name] = {
                "total_branches": len(all_branches),
                "stale_branches": len(stale_branches),
                "stale_branch_details": stale_branches,
                "deleted": []
            }
            
            if stale_branches:
                print(f"Repository: {repo_name}")
                print("Stale branches:")
                for i, (branch, age) in enumerate(stale_branches, 1):
                    print(f"{i}. {branch} (Last commit: {age} days ago)")
                
                to_delete = input("Enter branch numbers to delete (comma-separated, or 'all', 'none'): ").strip()
                if to_delete.lower() == "all":
                    selected_branches = [b[0] for b in stale_branches]
                elif to_delete.lower() == "none":
                    selected_branches = []
                else:
                    selected_branches = [stale_branches[int(i)-1][0] for i in to_delete.split(",") if i.isdigit()]
                
                delete_branches(repo, selected_branches)
                summary[repo_name]["deleted"] = selected_branches
                
                if len(selected_branches) == len(all_branches):
                    summary[repo_name]["recommend_delete_repo"] = True
        
        except Exception as e:
            print(f"Error processing {repo_name}: {e}")
    
    with open("cleanup_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
    
    print("Cleanup summary saved in cleanup_summary.json")

if __name__ == "__main__":
    main()
