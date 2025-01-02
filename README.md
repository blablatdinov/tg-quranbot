# Revive code bot

![](https://tokei.rs/b1/github/blablatdinov/revive-code-bot)
[![Hits-of-Code](https://hitsofcode.com/github/blablatdinov/revive-code-bot)](https://hitsofcode.com/github/blablatdinov/tg-quranbot/view)
![Connected repos](https://img.shields.io/endpoint?style=flat&url=https://revive-code-bot.ilaletdinov.ru/connected-repos/)
[![Webhook via ReHTTP](https://www.rehttp.net/b?u=https%3A%2F%2Frevive-code-bot.ilaletdinov.ru%2Fhook%2Fgithub)](https://www.rehttp.net/i?u=https%3A%2F%2Frevive-code-bot.ilaletdinov.ru%2Fhook%2Fgithub)

This bot is an automated tool designed to help maintain repositories by identifying and notifying about stagnant code files
that might require review. It assists in keeping your projects up-to-date and promotes regular code reviews to ensure code quality.

## How It Works

CodeReviewBot analyzes the commit history of files within your repository to identify files that have not been modified
for a certain period of time. When it detects such stagnant files, it creates an issue within the repository, suggesting that a
code review may be needed for those files.

## Features

- Automated identification of stagnant code files.
- Creation of issues for files that haven't been modified recently.
- Customizable time threshold for considering files as stagnant.
- Helps maintain code quality by encouraging regular reviews.
- Reduces the risk of having outdated or unmaintained code.

## Configure

You can install the bot either via GitHub Marketplace or manually.

### Option 1: Install via GitHub Marketplace (Recommended)

1. Visit the bot's GitHub [Marketplace page](https://github.com/marketplace/revive-code-bot).
2. Click Install and follow the prompts to grant access to the bot.
3. After installation, the bot will automatically start working with your repository.

### Option 2: Manual Installation

If you cannot use GitHub Marketplace, follow these two steps to configure the bot manually:

#### Step 1: Grant Access to the Bot

1. Open your GitHub repository.
2. Go to Settings > Collaborators and teams.
3. In the Collaborators section, click Invite a collaborator.
4. Enter the bot's GitHub username (e.g., `@revive-code-bot`) and send the invitation.

#### Step 2: Add a Webhook

1. Open your repository and go to Settings > Webhooks.
2. Click "Add webhook".
3. Use the following URL as the Payload URL:
`https://www.rehttp.net/p/https://revive-code-bot.ilaletdinov.ru/hook/github`
4. Set the Content type to `application/json`.
5. Select "Issue comments", "Issues", "Pushes" event as the trigger event.
6. Click "Add webhook" to save.

---

To configure the app, create a `.revive-code-bot.yml` file in the root of your repository with the following options:

```yaml
# Schedule when the bot checks for stagnant files (cron format)
# Visit https://crontab.guru
cron: '11 2 6 * *'  # Runs on the 6th day of each month at 02:11 AM

# Define file patterns to analyze using glob syntax
# glob: '**/*.py'  # Analyze all Python files
# glob: 'src/**/*.js'  # Analyze JavaScript files in the src directory and its subdirectories
glob: '**/*.py'  # Example: analyze all Python files

# Limit the maximum number of files listed in an issue
limit: 5
```

## See also:

[revive-scheduler](https://github.com/blablatdinov/revive-scheduler)
