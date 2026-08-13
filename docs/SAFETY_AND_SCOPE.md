# Safety and Scope

## Allowed use

- training mode;
- game-provided practice opponents;
- private sessions with informed, consenting friends;
- offline analysis of the user’s own recordings;
- user-supplied videos that may legally be used for the project.

## Disallowed use

- ranked or public matchmaking;
- automation against people who did not consent;
- memory reading or writing;
- game-process hooks or injection;
- network manipulation or packet inspection intended to control gameplay;
- anti-cheat evasion, bypass, or stealth techniques;
- hidden-state extraction;
- account farming, rewards farming, or unattended public play;
- automatic scraping of copyrighted gameplay libraries.

## Runtime safeguards

Live input requires all of the following:

1. explicit `--live-input` or equivalent opt-in;
2. non-default local calibration;
3. positive emulator-window focus verification;
4. fresh capture frames;
5. recognized active character where needed;
6. loaded action-rate limits;
7. working emergency-stop listener;
8. visible session indicator;
9. event recording enabled unless the user deliberately disables it for privacy.

Any failed precondition releases held keys and blocks further commands.

## Human-like constraints

The final system should support bounded reaction delay and decision rate. It must not exploit frame-perfect responses unavailable to a human observer. Difficulty control should be explicit and measurable.

## Data privacy

- capture only the calibrated emulator region;
- do not capture unrelated desktop content;
- store recordings locally by default;
- keep account identifiers out of logs when possible;
- provide future deletion and redaction tooling;
- never commit recordings, model checkpoints, or credentials.

## Responsible reporting

Do not claim:

- a mechanic is known when it is uncalibrated;
- a policy won when the match outcome was not reliably detected;
- self-play exists when only one side is controlled;
- a model works from an offline metric alone;
- video learning helped without a controlled comparison.
