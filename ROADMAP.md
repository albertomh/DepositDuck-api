# DepositDuck roadmap

## TODO

- [ ] find 'TODO's in code
- [ ] tweak existing release process so that next semver is already stated as [unreleased]
      in CHANGELOG and `just release` reads that instead of being handed a semver.
- [ ] automated releases (release-it?)
- [ ] add CD pipelines
- [ ] write script to check latest version of htmx & Bootstrap since they are vendored
- [ ] similarly, check for updates to GitHub actions
- [ ] customise FastAPI /docs favicon: <https://github.com/tiangolo/fastapi/issues/2581>
      for both apps

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
