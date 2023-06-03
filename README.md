# Adhoc Scheduler

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

This Home Assistant custom component allows you to schedule actions on an adhoc basis, either to run after a specified delay or at a specific time. As an added benefit, this integration also provides additional logbook entries, so you can easily track when a service was triggered by it. Another key feature is that schedules are saved to a file, ensuring they survive reboots and continue as planned.

**This integration will set up the following platforms.**

Platform | Description
-- | --
`sensor` | Show current number of pending actions

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `adhoc_scheduler`.
1. Download _all_ the files from the `custom_components/adhoc_scheduler/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Adhoc Scheduler"

## Usage

This custom component provides a new service `adhoc_scheduler.schedule` which you can call with various parameters to schedule an action.

- `name` (optional): A string that identifies your scheduled action.
- `action` (required): The action to be executed. It follows the same schema as the [action][action-syntax] part of an automation in Home Assistant.
- `delay`: A delay after which the action will be executed. This should be a positive time period.
- `trigger_time`: The exact time when the action will be triggered.
- `delay_from` (optional): The datetime from which the delay will be calculated.

Note: You must provide at either `delay` or `trigger_time`, but not both

Example, toggle an input boolean in 5 minutes from now
```
service: adhoc_scheduler.schedule
data:
  delay:
    minutes: 1
  action:
    service: input_boolean.toggle
    target:
      entity_id: input_boolean.test_toggle
```

Example: toggle an input boolean at 10:00:00
```
service: adhoc_scheduler.schedule
data:
  action:
    service: input_boolean.toggle
    target:
      entity_id: input_boolean.test_toggle
  trigger_time: "2023-06-04 10:00:00"
  name: "Toggle the Input Boolean"
  ```

## Logbook Integration
This custom component provides additional logbook entries each time a scheduled service is triggered. This allows you to track when a particular action was executed and helps in debugging and monitoring your scheduled actions.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[adhoc_scheduler]: https://github.com/Megabytemb/ha-adhoc-scheduler
[commits-shield]: https://img.shields.io/github/commit-activity/y/Megabytemb/ha-adhoc-scheduler.svg?style=for-the-badge
[commits]: https://github.com/Megabytemb/ha-adhoc-scheduler/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/Megabytemb/ha-adhoc-scheduler.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/Megabytemb/ha-adhoc-scheduler.svg?style=for-the-badge
[releases]: https://github.com/Megabytemb/ha-adhoc-scheduler/releases
[action-syntax]: https://www.home-assistant.io/docs/automation/action/