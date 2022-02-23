# Node.js application repository template

This is a simple node.js app that serves "hello world"

## Running the Humanitec initial setup

Use this repository as a template to create a new node.js application.
By running the workflow [setup-humanitec.yml](.github/workflows/setup-humanitec.yml), you can use Humanitec to deploy an inital version of this application.

### Prerequisite

The setup workflow requires your Humanitec Organization and Humanitec API token to be set as [repository secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-a-repository).

```
HUMANITEC_TOKEN = ...
HUMANITEC_ORG = ...
```

If you don't have an Humanitec account yet, you can register here: https://app.humanitec.io/

### Starting the Humanitec setup workflow

The setup is defined as a github action which can be triggered via a [manual trigger](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow).

The workflow requires the input of the Humanitec Application ID. This application id will be used to create a new application inside your Humanitec orgnaization and needs to be unique.

[Link to the Humanitec Documentation](https://docs.humanitec.com/)
