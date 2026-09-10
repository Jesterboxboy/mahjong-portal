# Mahjong Portal

## Documentation index

Detailed topic write-ups live in [.github/instructions/](.github/instructions/) (one file per topic, `*.instructions.md`).
These are **not** auto-loaded — read the relevant file with the Read tool when a task touches that area.

### Project basics
- [1_Mahjong_Portal_Project_Overview](.github/instructions/1_Mahjong_Portal_Project_Overview.instructions.md) — project purpose, system architecture, ETL pipeline, key technologies
- [2_Getting_Started_Local_Development_Deployment](.github/instructions/2_Getting_Started_Local_Development_Deployment.instructions.md) — local dev setup, Docker, deployment, Makefile commands
- [3_Application_Configuration_Settings](.github/instructions/3_Application_Configuration_Settings.instructions.md) — settings, env vars, Django config, production config
- [4_Core_Architecture](.github/instructions/4_Core_Architecture.instructions.md) — Django app structure, module organization, URL routing, system design
- [32_Glossary](.github/instructions/32_Glossary.instructions.md) — domain terminology, riichi mahjong concepts, project-specific abbreviations

### Players & accounts
- [5_Player_Data_Model_Profile_System](.github/instructions/5_Player_Data_Model_Profile_System.instructions.md) — player models, profiles, statistics, data structures
- [27_User_Accounts_Authentication](.github/instructions/27_User_Accounts_Authentication.instructions.md) — accounts, authentication, login, registration, permissions
- [29_Player_Profile_Templates](.github/instructions/29_Player_Profile_Templates.instructions.md) — player profile display templates, page layout, stats rendering

### Tournaments
- [6_Tournament_System](.github/instructions/6_Tournament_System.instructions.md) — tournament types, workflow, management
- [7_Tournament_Models_Registration](.github/instructions/7_Tournament_Models_Registration.instructions.md) — tournament models, player registration, data structures
- [8_Tournament_Admin_Result_Upload](.github/instructions/8_Tournament_Admin_Result_Upload.instructions.md) — tournament admin, result uploads, score management, admin UI
- [13_TournamentHandler_Round_Lifecycle](.github/instructions/13_TournamentHandler_Round_Lifecycle.instructions.md) — TournamentHandler, round lifecycle, game state, seating logic
- [30_Tournament_Rating_Templates](.github/instructions/30_Tournament_Rating_Templates.instructions.md) — tournament/rating display templates, results pages, rating tables

### Rating engine
- [9_Rating_Calculation_Engine](.github/instructions/9_Rating_Calculation_Engine.instructions.md) — rating calculation engine, pipeline, recalculation logic
- [10_Rating_Calculation_Algorithms_RR_EMA_CRR_Online](.github/instructions/10_Rating_Calculation_Algorithms_RR_EMA_CRR_Online.instructions.md) — RR, EMA, CRR, and online rating algorithms
- [11_TrueSkill_External_Ratings](.github/instructions/11_TrueSkill_External_Ratings.instructions.md) — TrueSkill algorithm and external rating system integrations

### Online automation & bots
- [12_Online_Tournament_Automation](.github/instructions/12_Online_Tournament_Automation.instructions.md) — online tournament automation, auto-pairing, online game processing, bots
- [14_Telegram_Discord_Bots](.github/instructions/14_Telegram_Discord_Bots.instructions.md) — Telegram/Discord bots for notifications and automation
- [15_Autobot_API_PortalAutoBot](.github/instructions/15_Autobot_API_PortalAutoBot.instructions.md) — Autobot API, PortalAutoBot, automated tournament control

### Pantheon integration
- [16_Pantheon_Integration](.github/instructions/16_Pantheon_Integration.instructions.md) — Pantheon tournament management system integration, data sync, API calls
- [17_Pantheon_API_Clients_Frey_Mimir](.github/instructions/17_Pantheon_API_Clients_Frey_Mimir.instructions.md) — Frey (player management) and Mimir (game results) API clients
- [18_Player_Synchronization_with_Pantheon](.github/instructions/18_Player_Synchronization_with_Pantheon.instructions.md) — player sync with Pantheon, identity matching, cross-system player management

### External platform integrations
- [19_Platform_Integrations_Tenhou_Mahjong_Soul](.github/instructions/19_Platform_Integrations_Tenhou_Mahjong_Soul.instructions.md) — Tenhou/Mahjong Soul integration, log import, game data parsing
- [20_Tenhou.net_Integration](.github/instructions/20_Tenhou.net_Integration.instructions.md) — Tenhou.net integration, log parsing, game import
- [21_Mahjong_Soul_Integration](.github/instructions/21_Mahjong_Soul_Integration.instructions.md) — Mahjong Soul integration, game log import, API usage

### Clubs, leagues & special competitions
- [22_Clubs_Leagues_Special_Events](.github/instructions/22_Clubs_Leagues_Special_Events.instructions.md) — clubs, leagues, special events, club-based tournament organization
- [23_Club_Management_Pantheon_Game_Sync](.github/instructions/23_Club_Management_Pantheon_Game_Sync.instructions.md) — club management features, syncing club games with Pantheon
- [24_League_System](.github/instructions/24_League_System.instructions.md) — league system, standings, seasons, management
- [25_Yagi_Keiji_Cup_Special_Competitions](.github/instructions/25_Yagi_Keiji_Cup_Special_Competitions.instructions.md) — Yagi Keiji Cup logic, special competition formats, custom rules
- [26_EMA_WRC_International_Qualification](.github/instructions/26_EMA_WRC_International_Qualification.instructions.md) — EMA, WRC qualification, international rating integration

### Frontend
- [28_Frontend_Templates](.github/instructions/28_Frontend_Templates.instructions.md) — Django frontend templates, HTML structure, template inheritance, UI components

### Background processing
- [31_Background_Tasks_Scheduled_Jobs](.github/instructions/31_Background_Tasks_Scheduled_Jobs.instructions.md) — background tasks, scheduled jobs, cron tasks, periodic processing
