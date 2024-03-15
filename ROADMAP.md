# DepositDuck roadmap

## TODO

- [ ] add CI pipelines - GitHub Actions
- [ ] sort out routine dependency patching (dependabot, etc.)
- [ ] automated releases (release-it?)
- [ ] add CD pipelines
- [ ] ensure auto `/docs` are disabled when not in debug mode
- [ ] write script to check latest version of htmx since it is vendored

## Feature wishlist

- Store copies of all documents used as RAG source material. Version this.
- Track which version of source material was used to generate answers.
- Track which version of relevant APIs + source material was used to generate answers.
- Scheduled process to automate updates to the RAG source material.
- Allow users to keep track of important documents relevant to their case.
- Suggest responses to
- Editable 'timeline builder' view that allows users to track events and is used to weave
  a narrative / history to load into the GPT's context window to act as a context / memory
  with which to generate relevant suggested courses of action / compose emails.  
- Important: above must handle detecting situations outside of tool's scope and be
  conservative in what it suggests.
